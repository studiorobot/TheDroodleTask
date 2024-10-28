from ..standardConversation.standardConversation import standardConversation #parent 
from ..conversationTools import encodeMessage, encodeMessageInternal #message encoder
from enum import Enum

class module(Enum):
    PASSIVE = 0
    PLAY  = 1
    TARGETED_OBSERVATION = 2
    STIMULATION = 3
    REFORMING = 4
    GROUNDING = 5
    CAPTIONING = 6
    REFINING = 7
    FEEDBACK = 8
    SELF_EVALUATION = 9
    AIDING = 10

    #Functions that check the attributes of each state
    def isDivergent(self) -> bool:
        return self in {module.PLAY, module.TARGETED_OBSERVATION, module.STIMULATION, module.REFORMING}
    
    def isConvergent(self) -> bool:
        return self in {module.GROUNDING, module.CAPTIONING, module.REFINING}
    
    def isAny(self) -> bool:
        return self in {module.FEEDBACK, module.SELF_EVALUATION, module.AIDING}
    
    #Get the list of neccessary before states to get to this module
    def prerequisites(self) -> list['module']:
        if (self == module.PLAY) or (self == module.TARGETED_OBSERVATION) or (self == module.AIDING) or (self == module.PASSIVE):
            return list(module.__members__.values()) #list of all possible enums
        elif self == module.STIMULATION:
            return {module.STIMULATION, module.TARGETED_OBSERVATION}
        elif self == module.REFORMING:
            return {module.REFORMING, module.TARGETED_OBSERVATION, module.CAPTIONING}
        elif self == module.GROUNDING:
            return {module.GROUNDING, module.REFORMING}
        elif self == module.CAPTIONING:
            return {module.CAPTIONING, module.GROUNDING}
        elif self == module.REFINING:
            return {module.REFINING, module.CAPTIONING}
        elif self == module.FEEDBACK:
            return {module.FEEDBACK, module.REFINING, module.CAPTIONING}
        elif self == module.SELF_EVALUATION:
            return {module.SELF_EVALUATION, module.REFINING, module.CAPTIONING}
        else:
            assert(False)

class modularConversation(standardConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], conversationName: str, savePath: str = 'conversationArchive'):
        super().__init__(model = model, prompts = constantPrompt + modulePrompts, conversationName = conversationName, savePath = savePath)
        
        self._constantPrompt = constantPrompt #prompts that hold true always
        self._modulePrompts = modulePrompts #prompts that switch out
        self._state = module(0) #the mode the chatbot is in, starts in the passive mode
        self._history = dict() #history of the used modules, used to limit possible steps

    #Check if switching into the proposed module is possible
    def checkSwitch(self, toModule: module) -> bool:
        #get list of prerequisites
        prereq = toModule.prerequisites()

        for indevModule in prereq: #loop through all prerequistes
            if self._history.get(indevModule, False) != False: #check if prerequisite is met
                return True
        return False #if no prerequisites met
    
    #attempts to switch the state to another module, returns true if successful
    def switchState(self, toModule: module) -> bool:
        if not self.checkSwitch(toModule):
            return False
        
        self._state = toModule

    #generates a list of all the possible next modules
    def allPossibleStates(self) -> list[module]:
        possibleModules = {}
        for indevModule in module:
            if self.checkSwitch(indevModule):
                possibleModules.append(indevModule)
        return possibleModules

    #loop through all the possible next modules and generate quick possible messages using them   
    def possibleNextMessages(self) -> list[dict]:
        possibleMessages = {}
        possibleModules = self.allPossibleStates()
        for indevModule in possibleModules:
            formattedPrompts = self._prepPrompts(self._constantPrompt+self._modulePrompts[indevModule.value])
            conversation = formattedPrompts + self._conversation
            message = self._makeRequest(tempConversation = conversation, model = "gpt-4o-mini")
            encodedMessage = encodeMessageInternal(message, "", "assistant-theoretical", "LLM", note = indevModule.name)
            possibleMessages.append(encodedMessage)
        return possibleMessages

    #Add a new entry into the module history
    def addHistory(self, newModule: module, index: int):
        #if module not in history, add a new list
        if self._history.get(newModule, False) == False:
            self._history[module] = {index}
        else: #if module is in history, add new entry to list
            self._history[module].append(index)

    #get the state of the chatbot
    def getState(self) -> module:
        return self._state
    
    #Adding history management into the insertMessage method
    def insertMessage(self, newMessage: str, role: str, imagePath: str = "", note: str = ""):
        super().insertMessage(newMessage, role, imagePath, note) #insert the message like normal
        self.addHistory(self._state, len(self._conversationInternal)) #add the history in

    #Prep the propmts for completion
    def _prepPrompts(self, prompts: list[str] = None) -> list[dict]:
        #if not overridden by entry value, assemble appropriate modular and constant prompts into list
        if prompts is None:
            prompts = self._constantPrompt + self._modulePrompts[self._state.value]
        return super()._prepPrompts(prompts) #make super do the rest