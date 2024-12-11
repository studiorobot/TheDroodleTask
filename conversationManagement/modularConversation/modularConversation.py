from ..standardConversation.standardConversation import standardConversation #parent 
from ..conversationTools.conversationTools import encodeMessage, encodeMessageInternal, removeImgInConv #message encoder
from enum import Enum #used to define the module states
import os #file management
from datetime import datetime #used to retrieve date and time for file name
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
        self.addHistory(module(0), 0)

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
    
    #switches the state to another module without checking prerequisites
    def switchStateUnbounded(self, toModule: module) -> bool:
        self._state = toModule

    #generates a list of all the possible next modules
    def recommendedNextStates(self) -> list[module]:
        possibleModules = []
        for indevModule in module:
            if self.checkRecommendedSwitch(indevModule):
                possibleModules.append(indevModule)
        return possibleModules
    
    # Generates a list of next messages for given modules
    def extrapolate(self, modules: list[module]) -> list[dict]:
        possibleMessages = []
        for indevModule in modules:
            # Prepare prompts without the image path
            formattedPrompts = self._prepPrompts(self._constantPrompt + [self._modulePrompts[indevModule.value]])
            conversation = formattedPrompts + removeImgInConv(self._conversation)  # Remove image from conversation
            
            # Generate response without vision processing
            message = self._makeRequest(tempConversation=conversation, model="gpt-4o-mini")
            
            # Encode message with module name but without image
            encodedMessage = encodeMessageInternal(message, "", "assistant-theoretical", "LLM", note=indevModule.name)
            possibleMessages.append(encodedMessage)
        return possibleMessages
    
    #Add a new entry into the module history
    def addHistory(self, newModule: module, index: int):
        #if module not in history, add a new list
        if self._history.get(newModule, False) == False:
            self._history[newModule] = [index]
        else: #if module is in history, add new entry to list
            self._history[newModule].append(index)

    #get the state of the chatbot
    def getState(self) -> module:
        return self._state
    
    #Adding history management into the insertMessage method
    def insertMessageDict(self, newMessage: dict):
        if newMessage.get("role") == "assistant":
            newMessage["note"] = self._state.name
        super().insertMessageDict(newMessage)
        self.addHistory(self._state, len(self._conversationInternal)) #add the history in

    #Prep the propmts for completion
    def _prepPrompts(self, prompts: list[str] = None) -> list[dict]:
        #if not overridden by entry value, assemble appropriate modular and constant prompts into list
        if prompts is None:
            prompts = self._constantPrompt + [self._modulePrompts[self._state.value]]
        return super()._prepPrompts(prompts) #make super do the rest
    
    #Update the image features
    def set_image_features(self, image_features):
        self.image_features = image_features  # Update features as needed

    #Update the current image
    def set_current_image(self, image_path):
        self.current_image = image_path

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

        return module(int(re.search(r'\d+', reply).group()))
    
    #Get the arguments for each module, speaking to each argument agent
    def get_module_arguments(self, modules: list[module]) -> list[dict]:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp

        #make a message containing the last two messages from the conversation
        formattedMessage = encodeMessageInternal(self._getLastTwoMessages(), timestamp, "user", "LLM")
        outputMessages = []

        #Call each agent to get their argument
        for agent in self._argument_agents:
            message = agent.contConversationDict(formattedMessage)
            outputMessages.append(message)
        return outputMessages
    
    #Main function for continuing the conversation using a message dict object
    def contConversationDict(self, newMessage: dict) -> dict:
        self.insertMessageDict(newMessage) #Add new message
        self.switchStateUnbounded(self.decideSwitch()) #Switch the state
        outMessage = self.turnoverConversationDict()
        return outMessage
    
    #Helper function to get the last two messages as a string
    def _getLastTwoMessages(self) -> str:
        #get the last two messages (or one if there is only one)
        if len(self._conversationInternal) >= 2:
            lastMessages = self._conversationInternal[-2:] #get the last two messages
        else:
            lastMessages = self._conversationInternal[-1:] #get the last message
        
        #Format the output
        output = ""
        for message in lastMessages:
            output = output + message.get("role")
            output = output + "> "
            output = output + message.get("content") + "\n"
        return output
    
    #Helper function that returns a list of all modules
    def allModules(self) -> list['module']:
        return list(module.__members__.values())