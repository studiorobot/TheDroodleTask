import tiktoken #used to track api request tokens
import time #used to track time
import logging #used to log messages
from conversationManagement.conversationTools import conversationErrors #error handling

#The point of this class is to create a unified object that is in charge of keeping track of token counts so that we don't go over the limit
class tokenTracker():
    def __init__(self, tokenLimit = {"gpt-4o": 20000, "gpt-4o-mini": 150000, "o1": 20000}):
        self._tokenHistory = [] #init token history
        self._tokenLimit = tokenLimit #init token limit

    #Add a message and context to the token history. Can take either string or conversation history in openAI format
    def addTokenHistory(self, textIn, model: str):
        encoding = tiktoken.encoding_for_model(model)
        tokenCount = 0
        if isinstance(textIn, str):
            tokenCount = len(encoding.encode(textIn))
        elif isinstance(textIn, list):
            for message in textIn:
                tokenCount += len(encoding.encode(message.get("content")[0].get("text")))
        else:
            logging.warning("token count not calculated")
        
        self._tokenHistory.append({"message": tokenCount, "time": time.time(), "model":model}) #add tokens to history

    #count the tokens sent in the last minute
    def getTokensLastMinute(self, model: str) -> int:
        currentTime = time.time()
        tokenCount = 0
        for token in self._tokenHistory:
            if currentTime - token.get("time") < 60 and token.get("model") == model:
                tokenCount += token.get("message")
        return tokenCount
    
    #check if a new request is going to work
    def checkTokenLimit(self, model: str):
        if self.getTokensLastMinute(model) > self._tokenLimit.get(model):
            raise conversationErrors.slowDownError(f"the token count of {self.getTokensLastMinute(model)} in the last minute exceeds limit of {self._tokenLimit.get(model)}")