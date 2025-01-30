from ..standardConversation.standardConversation import standardConversation #parent 
from ..asyncConversation.asyncConversation import asyncConversation #async agents
from ..conversationTools.conversationTools import encodeMessageInternal, getTimeStamp, extract_features #message encoder
from ..conversationTools import conversationErrors #error handling
from ..conversationTools.tokenTracker import tokenTracker #token tracking
from enum import Enum #used to define the module states
from io import StringIO #used to control string streams
import os #file management
import re #used to do a better extraction from controller responses
import logging #used to log errors and notes
import time #used to time total system responses
import asyncio #used to call async functions

class module(Enum):
    PLAY  = 0
    TARGETED_OBSERVATION = 1
    STIMULATION = 2
    REFORMING = 3
    GROUNDING = 4
    CAPTIONING = 5
    REFINING = 6
    AIDING = 7

    #Functions that check the attributes of each state
    def isDivergent(self) -> bool:
        return self in {module.PLAY, module.TARGETED_OBSERVATION, module.STIMULATION, module.REFORMING}
    
    def isConvergent(self) -> bool:
        return self in {module.GROUNDING, module.CAPTIONING, module.REFINING}
    
    def isAny(self) -> bool:
        return self == module.AIDING

class modularConversation(standardConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], controlPrompts: list[str], conversationName: str, savePath: str = 'conversationArchive', imageFeatures: str = "", lowerModel: str = "gpt-4o-mini"):
        #Make some invariant assertions
        if len(modulePrompts) != len(module):
            raise conversationErrors.ImproperPromptFormatError("Module prompts must be equal to the number of modules")
        if len(controlPrompts) != 2:
            raise conversationErrors.ImproperPromptFormatError("Control prompts must be of length 2")
        if len(constantPrompt) <= 0:
            raise conversationErrors.InvalidInitVariableError("Constant prompts must have at least one prompt")
        
        #new directory for the modular conversation
        savePath = savePath+"/modularConversation - "+conversationName

        #Create the save path if it does not exist
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        #Init parent class
        super().__init__(model = model, prompts = constantPrompt + modulePrompts, conversationName = conversationName, savePath = savePath, tokenTracker = tokenTracker())
        
        self._constantPrompt = constantPrompt #prompts that hold true always
        self._modulePrompts = modulePrompts #prompts that switch out
        self._state = module(0) #the mode the chatbot is in, starts in the play mode
        self._lowerModel = lowerModel #model used low level decision making
        self._history = dict() #history of the used modules, used to limit possible steps
        self._image_features = imageFeatures  # Pre-processed image features, if provided
        self._current_image = "" #current image path
        self._recordHistory()

        #Create CONTROL agent
        self._controller = standardConversation(model, [controlPrompts[0]], conversationName + " - CONTROLLER", savePath, self._tokenTracker)

        # Create SPEAKING agents for each module
        self._speaking_agents = []
        for indevModule in self.allModules():
            agent_name = conversationName + " - " + str(indevModule.value) + " " + indevModule.name + " - Speaking" #name
            
            #prompts for the agent
            agent_prompt = []
            for prompt in self._constantPrompt:
                agent_prompt.append(prompt)
            agent_prompt.append(self._modulePrompts[indevModule.value])

            #make and add the agent
            agent = standardConversation(model, agent_prompt, agent_name, savePath, self._tokenTracker)
            self._speaking_agents.append(agent)

        # Create ARGUMENT agents for each module
        self._argument_agents = []
        for indevModule in self.allModules():
            agent_name = conversationName + " - " + str(indevModule.value) + " " + indevModule.name + " - Arguing" #name
            agent_prompt = [controlPrompts[1], modulePrompts[indevModule.value]]
            agent = asyncConversation(lowerModel, agent_prompt, agent_name, savePath, self._tokenTracker)
            self._argument_agents.append(agent)
    
    #DECISION MAKING--------------------------------------------------------

    #Get the arguments for each module, speaking to each argument agent
    async def get_module_arguments(self, modules: list[module]) -> list[dict]:
        #make a message containing the last two messages from the conversation
        formattedMessage = encodeMessageInternal(self._getLastMessages(2), getTimeStamp(), "user", "LLM")
        tasks = []

        try:
            #Call each agent to get their argument
            for agent in self._argument_agents:
                tasks.append(agent.asyncContConversationDict(formattedMessage))
            outputMessages = await asyncio.gather(*tasks)
        except conversationErrors.slowDownError:
            logging.warning("Slowdown complete, redirected to non-parallel requests")
            #Call each agent to get their argument
            for agent in self._argument_agents:
                message = agent.contConversationDict(formattedMessage)
                outputMessages.append(message)

        return outputMessages

    # Gets given module to talk
    def makeModuleSpeak(self, module_in: module) -> dict:
        #Get new messages since module last spoke
        lastModuleIndex = self._getLastModuleIndex(module_in)
        if lastModuleIndex == -1: #if no history, get all messages
            lastMessages = self._getLastMessages()
        else: #if history, get messages from when last spoke
            lastMessages = self._getLastMessages(self.getIndex()-lastModuleIndex+1)

        #Make request to module speaking agent
        agent = self._speaking_agents[module_in.value]
        agent.cleanOutImages() #remove images from the conversation
        message = encodeMessageInternal(lastMessages, getTimeStamp(), "user", "LLM", image= self._current_image)
        logging.info("Last Module Index: "+str(lastModuleIndex) + " Current Index: "+str(self.getIndex()))
        return agent.contConversationDict(message)
    
    #Retrive the controller given by the index and get their decision
    def decideSwitch(self) -> module:
        #Get the chat history
        message = self.getConversationStr()

        #make and append the arguments
        #Add marker
        message = message + "Examples:\n"

        #get arguments
        possibleModules = self.allModules()
        arguments = asyncio.run(self.get_module_arguments(possibleModules))

        #put all the arguments in one string
        argumentStr = ""
        for i in range(len(possibleModules)):
            possibleMessage = arguments[i]
            indevModule = possibleModules[i]
            argumentStr = argumentStr + "Assistant - " + indevModule.name + "(" + str(indevModule.value) + ")> "+possibleMessage.get("content")+"\n"

        #append arguments
        message = message + "\n\n" + argumentStr
        
        #Package the new message
        messageDict = encodeMessageInternal(message, "", "user", "controller")
        
        #make the request
        reply = self._controller.contConversationDict(messageDict).get("content")

        return self._extract_module(reply)
    
    #CONVERSATION MANAGEMENT------------------------------------------------

    #Adding history management into the insertMessage method
    def insertMessageDict(self, newMessage: dict):
        #Update the image features if new image present
        if newMessage.get("image_path") != "":
            self.set_current_image(newMessage.get("image_path"))

        #Add the module name to the note
        if newMessage.get("role") == "assistant":
            newMessage["note"] = self._state.name
        super().insertMessageDict(newMessage)

        if(newMessage.get("role") == "assistant"):
            self._recordHistory() #add the history in
    
    #Main function for continuing the conversation using a message dict object
    def contConversationDict(self, newMessage: dict) -> dict:
        startTime = time.time() #start the timer

        self.insertMessageDict(newMessage) #Add new message
        self._switchStateUnbounded() #Switch the state
        outMessage = self.turnoverConversationDict()

        logging.info("TOTAL RESPONSE TIME: "+str(time.time()-startTime))
        return outMessage
    
    #Get a response from the LLM and store it without a human input, modified to use multiple agents
    def _makeRequest(self, tempConversation: list[dict] = None, model: str = None) -> str:
        #Throw if _makeRequest is used improperly
        if tempConversation != None or model != None:
            raise conversationErrors.ConversationError("Modular conversation does not support conversation or model changes")
        
        return self.makeModuleSpeak(self.getState()).get("content") #make the module speak

    #Update the current image
    def set_current_image(self, image_path: str):
        self._current_image = image_path
        self._image_features = extract_features(self._client, "gpt-4o", image_path)

    #Add a new entry into the module history
    def _recordHistory(self):
        #get the current module and index
        current_module = self.getState()
        index = self.getIndex()

        #if module not in history, add a new list
        if self._history.get(current_module, False) == False:
            self._history[current_module] = [index]
        else: #if module is in history, add new entry to list
            self._history[current_module].append(index)

    #Get the last index of a module's use in the history
    def _getLastModuleIndex(self, module_in: module) -> int:
        if self._history.get(module_in, False) == False:
            return -1
        else:
            return self._history[module_in][-1]

    #switches the state to another module
    def _switchStateUnbounded(self) -> bool:
        #Try to get state to switch to
        try:
            toModule = self.decideSwitch()
        except conversationErrors.moduleExtractError or conversationErrors.SwitchOutOfBoundsError:
            logging.warning("Error in switching state, keeping current state")
            return False
        
        #Switch the state
        self._state = toModule
        logging.info("Switched to module: "+toModule.name)
        return True
    
    def makeConversationSave(self):
        # make the new directory one level higher than the save path
        parent_save_path = os.path.dirname(self._savePath)
        savePath = os.path.join(parent_save_path, "modularConversation - " + self._conversationName + self._idNumber)
        os.mkdir(savePath)

        # Save the core conversation
        super().makeConversationSave(savePath)

        # Save the controller
        self._controller.makeConversationSave(savePath)

        # Save the speaking agents
        for agent in self._speaking_agents:
            agent.makeConversationSave(savePath)

        # Save the argument agents
        for agent in self._argument_agents:
            agent.makeConversationSave(savePath)
        
        # Save the log
        logPath = os.path.join(savePath, "main_log"+ self._idNumber +".log")

        #Retrive log stream from logging
        log_stream = None
        for handler in logging.getLogger().handlers: 
            log_stream = getattr(handler, "stream", None) #get log storage from logger
            if isinstance(log_stream, StringIO):
                break
            else:
                log_stream = None
        
        if log_stream != None:
            with open(logPath, "w") as file:
                file.write(log_stream.getvalue()) #write storage
        else:
            logging.warning("Tried to save log to file but no log storage was set up")
    
    #HELPERS---------------------------------------------------------------
    
    #Helper function to get the last two messages as a string
    def _getLastMessages(self, number: int = None) -> str:
        #get the last messages (or one if there is only one)
        if number == None or len(self._conversationInternal) < number:
            lastMessages = self._conversationInternal
        else:
            lastMessages = self._conversationInternal[-number:]
        
        #Format the output
        output = ""
        for message in lastMessages:
            output = output + message.get("role")
            output = output + "> "
            output = output + message.get("content") + "\n"
        return output
    
    def _extract_module(self, reply: str):
        match = re.search(r'\d+', reply)
        if not match:
            #No number in the response
            raise conversationErrors.moduleExtractError("No digits found in message to determine the module.")
        elif int(match.group()) > len(module) or int(match.group()) < 0:
            #Number out of bounds
            raise conversationErrors.SwitchOutOfBoundsError("Module out of bounds")
        else:
            return module(int(match.group()))
    
    #ACCESSORS--------------------------------------------------------------
    
    #Helper function that returns a list of all modules
    def allModules(self) -> list['module']:
        return list(module.__members__.values())
    
    #get the state of the chatbot
    def getState(self) -> module:
        return self._state
    
    #get the index of the conversation
    def getIndex(self) -> int:
        #The main internal conversation storage includes:
        # - The constant prompts (number equal to length of init array)
        # - All messages
        return len(self._conversationInternal)-len(self._constantPrompt)