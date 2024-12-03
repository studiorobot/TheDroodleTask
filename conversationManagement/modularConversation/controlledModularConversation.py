from ..modularConversation.modularConversation import modularConversation, module #parent 
from ..standardConversation.standardConversation import standardConversation #controller 
from ..conversationTools import encodeMessage, encodeMessageInternal #message encoder
import re #used to do a better extraction from controller responses

class controlledModularConversation(modularConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], controlPrompt: str, conversationName: str, savePath: str = 'conversationArchive', imageFeatures=None):
        super().__init__(model, constantPrompt, modulePrompts, conversationName, savePath)
        self._controller = standardConversation(model, [controlPrompt], conversationName + " - Controller", savePath)
        self.image_features = imageFeatures  # Pre-processed image features, if provided

    def set_image_features(self, image_features):
        self.image_features = image_features  # Update features as needed

    def set_current_image(self, image_path):
        self.current_image = image_path

    # Retrive the controller given by the index and get their decision
    def decideSwitch(self) -> module:
        #Get the chat history
        message = self.getConversationStr()

        #make and append the extrapolations
        #Add marker
        message = message + "Examples:\n"

        #get extrapolations
        possibleModules = self.allModules()
        extrapolations = self.extrapolate(possibleModules)
        

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
        self.switchStateUnbounded(self.decideSwitch()) #Switch the state
        outMessage = self.turnoverConversationDict()
        return outMessage