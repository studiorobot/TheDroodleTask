from ..standardConversation.standardConversation import standardConversation #parent 
from ..conversationTools.conversationTools import encodeMessage, encodeMessageInternal, removeImgInConv, getTimeStamp #message encoder
from ..conversationTools import conversationErrors #error handling
from enum import Enum #used to define the module states
import os #file management
import re #used to do a better extraction from controller responses

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
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], controlPrompts: list[str], conversationName: str, savePath: str = 'conversationArchive', imageFeatures=None):
        #Make some invariant assertions
        assert len(modulePrompts) == len(module), "Module prompts must be equal to the number of modules"
        assert len(controlPrompts) == 2, "Control prompts must be of length 2"
        assert len(constantPrompt) > 0, "Constant prompts must have at least one prompt"
        
        #make the new directory for the modular conversation
        savePath = savePath+"/modularConversation - "+conversationName
        os.mkdir(savePath)

        #Init parent class
        super().__init__(model = model, prompts = constantPrompt + modulePrompts, conversationName = conversationName, savePath = savePath)
        
        self._constantPrompt = constantPrompt #prompts that hold true always
        self._modulePrompts = modulePrompts #prompts that switch out
        self._state = module(0) #the mode the chatbot is in, starts in the play mode
        self._history = dict() #history of the used modules, used to limit possible steps
        self.image_features = imageFeatures  # Pre-processed image features, if provided
        self._recordHistory()

        #Create CONTROL agent
        self._controller = standardConversation(model, [controlPrompts[0]], conversationName + " - Controller", savePath)
        
        # Create SPEAKING agents for each module
        self._speaking_agents = []
        for indevModule in self.allModules():
            agent_name = conversationName + " - " + indevModule.name #name
            
            #prompts for the agent
            agent_prompt = []
            for prompt in self._constantPrompt:
                agent_prompt.append(prompt)
            agent_prompt.append(self._modulePrompts[indevModule.value])

            #make and add the agent
            agent = standardConversation(model, agent_prompt, agent_name, savePath)
            self._speaking_agents.append(agent)

        # Create ARGUMENT agents for each module
        self._argument_agents = []
        for indevModule in self.allModules():
            agent_name = conversationName + " - " + indevModule.name
            agent_prompt = [controlPrompts[1], modulePrompts[indevModule.value]]
            agent = standardConversation(model, agent_prompt, agent_name, savePath)
            self._argument_agents.append(agent)
    
    #DECISION MAKING--------------------------------------------------------

    #Get the arguments for each module, speaking to each argument agent
    def get_module_arguments(self, modules: list[module]) -> list[dict]:
        #make a message containing the last two messages from the conversation
        formattedMessage = encodeMessageInternal(self._getLastMessages(2), getTimeStamp(), "user", "LLM")
        outputMessages = []

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
            lastMessages = self._getLastMessages(self.getIndex()-lastModuleIndex)
        
        #Make request to module speaking agent
        agent = self._speaking_agents[module_in.value]
        message = encodeMessageInternal(lastMessages, getTimeStamp(), "user", "LLM")
        return agent.contConversationDict(message)
    
    #Retrive the controller given by the index and get their decision
    def decideSwitch(self) -> module:
        #Get the chat history
        message = self.getConversationStr()

        #make and append the extrapolations
        #Add marker
        message = message + "Examples:\n"

        #get extrapolations
        possibleModules = self.allModules()
        extrapolations = self.get_module_arguments(possibleModules)
        

        #put all the extrapolations in one string
        extrapolationsStr = ""
        for i in range(len(possibleModules)):
            possibleMessage = extrapolations[i]
            indevModule = possibleModules[i]
            extrapolationsStr = extrapolationsStr + "Assistant - " + indevModule.name + "(" + str(indevModule.value) + ")> "+possibleMessage.get("content")+"\n"

        #append extrapolations
        message = message + "\n\n" + extrapolationsStr
        
        #Package the new message
        messageDict = encodeMessageInternal(message, "", "user", "Controller")
        
        #make the request
        reply = self._controller.contConversationDict(messageDict).get("content")

        return self._extract_module(reply)
    
    #CONVERSATION MANAGEMENT------------------------------------------------

    #Adding history management into the insertMessage method
    def insertMessageDict(self, newMessage: dict):
        if newMessage.get("role") == "assistant":
            newMessage["note"] = self._state.name
        super().insertMessageDict(newMessage)
        self._recordHistory() #add the history in
    
    #Main function for continuing the conversation using a message dict object
    def contConversationDict(self, newMessage: dict) -> dict:
        self.insertMessageDict(newMessage) #Add new message
        self._switchStateUnbounded() #Switch the state
        outMessage = self.turnoverConversationDict()
        return outMessage
    
    #Get a response from the LLM and store it without a human input, modified to use multiple agents
    def turnoverConversationDict(self) -> dict:
        return self.makeModuleSpeak(self.getState()) #make the module speak
    
    #Update the image features
    def set_image_features(self, image_features):
        self.image_features = image_features  # Update features as needed

    #Update the current image
    def set_current_image(self, image_path):
        self.current_image = image_path

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
        except conversationErrors.moduleExtractError:
            return False
        
        #Switch the state
        self._state = toModule
        return True
    
    #HELPERS---------------------------------------------------------------
    
    #Helper function to get the last two messages as a string
    def _getLastMessages(self, number: int = None) -> str:
        #get the last messages (or one if there is only one)
        if len(self._conversationInternal) < number or number == None:
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
    
    def _extract_module(reply: str):
        match = re.search(r'\d+', reply)
        if match:
            return module(int(match.group()))
        else:
            raise conversationErrors.moduleExtractError("No digits found in message to determine the module.")
    
    #ACCESSORS--------------------------------------------------------------
    
    #Helper function that returns a list of all modules
    def allModules(self) -> list['module']:
        return list(module.__members__.values())
    
    #get the state of the chatbot
    def getState(self) -> module:
        return self._state
    
    #get the index of the conversation
    def getIndex(self) -> int:
        return len(self._conversationInternal)-1