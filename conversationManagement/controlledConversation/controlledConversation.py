from ..standardConversation.standardConversation import standardConversation #parent 
from ..conversationTools import encodeMessage

class controlledConversation(standardConversation):
    def __init__(self, chatModel: str, controlModel: str, chatPrompts: list[str], controlPrompts: list[str], conversationName: str, savePath: str = "conversationArchive"):
        super().__init__(chatModel, chatPrompts, conversationName, savePath) #run init for parent class to access api, set up files, and init message files

        self._controlModel = controlModel
        
        #Construct the prompt list for the conversation controller
        self._controlPrompts = []
        for prompt in controlPrompts:
            self._controlPrompts.append(prompt)

    #Function that takes a look at the conversation and returns a judement
    def makeJudegement(self) -> str:
        #make a copy of the conversation without any system inserts
        tempConversation = []
        for message in self._conversation:
            if message['role'] != "system":
                tempConversation.append(message)
        
        tempConversation = self._prepPrompts(self._controlPrompts) + tempConversation

        return self.makeRequest(tempConversation, self._controlModel)
       
    def contConversation(self, newMessage: str, imagePath: str = "") -> str:
        self.insertMessage(newMessage, "user", imagePath) #Add new text and possible image message to history

        judgement = self.makeJudegement() #make a judgement based on the new human message
        print("\n\nJudgement> "+judgement)
        self.insertMessage(judgement, "system", altRoleName="judgementSystemInsert") #insert the judgement as a system message

        outputMessage = self.makeRequest() #Make request to regular chat model
        self.insertMessage(outputMessage, "assistant") #Add assistant message to history

        return outputMessage
    
    #Returns prompts in controll of the interaction/used to make judements
    def getControlPrompts(self) -> list[str]:
        return self._controlPrompts