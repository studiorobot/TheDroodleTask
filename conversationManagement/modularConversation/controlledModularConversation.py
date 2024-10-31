from ..modularConversation.modularConversation import modularConversation #parent 
from ..standardConversation.standardConversation import standardConversation #controller 
from ..conversationTools import encodeMessage, encodeMessageInternal #message encoder
import re #used to do a better extraction from controller responses

class multiControlledModularConversation(modularConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], controlPrompts: list[str], controlTypes: list[str], conversationName: str, savePath: str = 'conversationArchive'):
        #init modular conversation as normal
        super().__init__(model, constantPrompt, modulePrompts, conversationName, savePath)
        
        #Save control types
        self._controlTypes = controlTypes

        #make an array of controllers using the prompts given as paramaters
        self._controllers = []
        for i in range(len(controlPrompts)):
            controller = standardConversation(model, [controlPrompts[i]], conversationName+" - Controller " + controlTypes[i], savePath)
            self._controllers.append(controller)

    #Retrive all controllers and retrive their decisions, returning them as an array
    def decideAllSwitch(self) -> list[int]:
        allDecisions = []
        #Call all decideSwitch indecies
        for index in range(len(self._controllers)):
            decision = self.decideSwitch(index)
            allDecisions.append(decision)
        return allDecisions

    #Retrive the controller given by the index and get their decision
    def decideSwitch(self, index: int) -> int:
        #Get the chat history
        message = self.getConversationStr()

        #if extrapolations, make and append those
        if self._controlTypes[index] == "extrapolation":
            #Add marker
            message = message + "Examples:\n"
            #get extrapolations
            extrapolations = self.possibleNextMessages()
            possibleModules = self.allPossibleStates()

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
        reply = self._controllers[index].contConversationDict(messageDict).get("content")

        return int(re.search(r'\d+', reply).group())