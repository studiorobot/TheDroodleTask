from ..standardConversation.standardConversation import standardConversation #parent 
from ..conversationTools.conversationTools import encodeMessage, encodeMessageInternal, removeImgInConv #message encoder
from enum import Enum

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
    
    #Get the list of neccessary before states to get to this module
    def prerequisites(self) -> list['module']:
        if (self == module.PLAY) or (self == module.TARGETED_OBSERVATION) or (self == module.AIDING):
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
        else:
            assert(False)


class modularConversation(standardConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], conversationName: str, savePath: str = 'conversationArchive'):
        super().__init__(model = model, prompts = constantPrompt + modulePrompts, conversationName = conversationName, savePath = savePath)
        
        self._constantPrompt = constantPrompt #prompts that hold true always
        self._modulePrompts = modulePrompts #prompts that switch out
        self._state = module(0) #the mode the chatbot is in, starts in the play mode
        self._history = dict() #history of the used modules, used to limit possible steps
        self.addHistory(module(0), 0)
        self._historyLimit = 7 #limit of the history for module limitations

    #returns a list of all modules
    def allModules(self) -> list['module']:
        return list(module.__members__.values())
    
    #Check if switching into the proposed module is possible
    def checkRecommendedSwitch(self, toModule: module) -> bool:
        #get list of prerequisites
        prereq = toModule.prerequisites()
        curentIndex = len(self._conversationInternal)

        for indevModule in prereq: #loop through all prerequistes
            moduleHistory = self._history.get(indevModule, [])
            if moduleHistory != [] and (max(moduleHistory) - curentIndex) < self._historyLimit: #check if prerequisite is met
                return True
        return False #if no prerequisites met
    
    #attempts to switch the state to another module, returns true if successful
    def switchStateBounded(self, toModule: module) -> bool:
        if not self.checkRecommendedSwitch(toModule):
            return False
        
        self._state = toModule

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