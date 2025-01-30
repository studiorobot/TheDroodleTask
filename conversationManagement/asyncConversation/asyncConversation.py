from ..standardConversation.standardConversation import standardConversation #parent 
import asyncio #used to make async functions
import aiohttp #used to make async requests
import logging #used to log messages
import time #used to time api responses

from conversationManagement.conversationTools.conversationTools import encodeMessageInternal, getTimeStamp #tools for conversation
from conversationManagement.conversationTools import conversationErrors #error handling
from conversationManagement.conversationTools.tokenTracker import tokenTracker #token tracking

class asyncConversation(standardConversation):
    def __init__(self, model: str, prompts: list[str], conversationName: str, savePath: str = 'conversationArchive', tokenTracker: tokenTracker = None):
        super().__init__(model, prompts, conversationName, savePath, tokenTracker)
    
    #Async version of the make request function
    async def _asyncMakeRequest(self, tempConversation: list[dict] = None, model: str = None) -> str:
        #If conversation is allowed to default, use the conversation in the class instance and put the intial prompts at the start
        if tempConversation is None:
            tempConversation = self._prepPrompts() + self._conversation

        #if model is allowed to default, use the model given in class init
        if model is None:
            model = self._model

        #If there have been too many tokens sent in the last minute, throw error
        self._tokenTracker.checkTokenLimit(model)

        self._tokenTracker.addTokenHistory(tempConversation, model) #add tokens to history
        
        logging.info(f"request made using {model} with {self._tokenTracker.getTokensLastMinute(model)} tokens in history:" + str(tempConversation)+"\n")

        startTime = time.time()

        if self._usingUmichApi:
            raise conversationErrors.slowDownError("Umich API not supported for asyncConversation")\
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._client.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": tempConversation
                }
            ) as response:
                response_json = await response.json()
                output = response_json['choices'][0]['message']['content']
        
        duration = time.time() - startTime
        duration_str = f"{duration:.2f} seconds"
        self._tokenTracker.addTokenHistory(output, model) #add tokens to history
        logging.info(f"response received in {duration_str} with {self._tokenTracker.getTokensLastMinute(model)} tokens in history: " + output+"\n") #log response and time

        return output
    
    async def asyncTurnoverConversationDict(self):
        #Get the last message from storage
        lastMessage = self._conversationInternal[-1]

        #Recursievely try to make a request to the LLM
        iterations = 0
        while True:
            iterations += 1
            try:
                outputMessageText = await self._asyncMakeRequest() #Make request to chat model
                break
            except conversationErrors.slowDownError as e:
                logging.warning(f"Slow down error caught, waiting {10*iterations} seconds before trying again")
                time.sleep(10*iterations); #wait 10 seconds before trying again
            if iterations > 6:
                raise conversationErrors.slowDownError("Too many slow down errors")
            
        timestamp = getTimeStamp() #get timestamp
        assistantType = lastMessage.get("assistant_type")
        outputMessage = encodeMessageInternal(outputMessageText, timestamp, "assistant", assistantType) #package message

        self.insertMessageDict(outputMessage)
        return outputMessage
    
    async def asyncContConversationDict(self, newMessage: dict) -> dict:
        self.insertMessageDict(newMessage) #Add new message
        outMessage = await self.asyncTurnoverConversationDict()
        return outMessage