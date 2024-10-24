from ..standardConversation.standardConversation import standardConversation #parent 
from ..conversationTools import encodeMessage #message encoder
from ..eliza.eliza import Eliza #eliza response system https://github.com/wadetb/eliza
import time #for delay function
import random #randomness for delay function

class elizaConversation(standardConversation):
    def __init__(self, conversationName: str, savePath: str = 'conversationArchive'):
        super().__init__(model = None, prompts = None, conversationName = conversationName, savePath = savePath)

    def _makeRequest(self, tempConversation: list[dict] = None, model: str = None) -> str:
        #if model is allowed to default, use the model given in class init
        if model is not None:
            super()._makeRequest(tempConversation, model)

        #DELAY
        time.sleep(random.uniform(1, 3))

        #If conversation is allowed to default, use the conversation in the class instance
        if tempConversation is None:
            tempConversation = self._conversation

        #init eliza
        elizaBot = Eliza()
        elizaBot.load('conversationManagement/eliza/doctor.txt')

        #retrive last message from conversation (in openAI format) and get response
        lastMessage = tempConversation[-1].get("content")[0].get("text")
        return elizaBot.respond(lastMessage)


        
