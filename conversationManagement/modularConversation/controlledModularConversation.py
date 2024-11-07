from ..modularConversation.modularConversation import modularConversation, module #parent 
from ..standardConversation.standardConversation import standardConversation #controller 
from ..conversationTools import encodeMessage, encodeMessageInternal #message encoder
import re #used to do a better extraction from controller responses

class controlledModularConversation(modularConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], controlPrompt: str, conversationName: str, savePath: str = 'conversationArchive'):
        #init modular conversation as normal
        super().__init__(model, constantPrompt, modulePrompts, conversationName, savePath)

        #make a controller using the parameters given
        self._controller = standardConversation(model, [controlPrompt], conversationName+" - Controller", savePath)

    #Retrive the controller given by the index and get their decision
    def decideSwitch(self) -> module:
        #Get the chat history
        message = self.getConversationStr()

        #make and append the extrapolations
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
        reply = self._controller.contConversationDict(messageDict).get("content")

        return module(int(re.search(r'\d+', reply).group()))
    
    #Main function for continuing the conversation using a message dict object
    def contConversationDict(self, newMessage: dict) -> dict:
        self.insertMessageDict(newMessage) #Add new message
        self.switchState(self.decideSwitch()) #Switch the state
        outMessage = self.turnoverConversationDict()
        return outMessage