import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('../../')) #Sets path to project folder

from openai import OpenAI #GPT resources
from openai import AzureOpenAI #umich GPT access point
from dotenv import load_dotenv #used to pull api key from .env file
from rich import print #update the print function to include more colors
from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from datetime import datetime #used to retrieve date
import json #used to store messages in json files
import logging #used to log messages
import time #used to time api responses
import random #used to add randomness to the time flattening

from conversationManagement.conversationTools.conversationTools import encodeMessage, encodeMessageInternal, getTimeStamp, makeID, removeImgInConv #tools for conversation
from ..conversationTools import conversationErrors #error handling
from ..conversationTools.tokenTracker import tokenTracker #token tracking for api requests

class standardConversation:

    def __init__(self, model: str, prompts: list[str], conversationName: str, savePath: str = 'conversationArchive', tokenTracker: tokenTracker = None, timeFlattening: int = 0):
        #Make some invariant assertions
        if not isinstance(prompts, list):
            raise conversationErrors.ImproperPromptFormatError("Prompts must be in a list")
        if not isinstance(conversationName, str):
            raise conversationErrors.InvalidInitVariableError("Conversation name must be a string")
        
        #define instance variables from function call
        self._model = model
        self._prompts = prompts
        self._conversationName = conversationName
        self._idNumber = makeID()
        self._savePath = savePath
        self._timeFlattening = timeFlattening
        self._tempFilePath = "./" + savePath + "/" + conversationName + " - temp.json"
        self._conversation = [] #important conversation variable for openAI
        self._conversationInternal = [] #conversation variable for our storage

        if tokenTracker is None:
            from ..conversationTools.tokenTracker import tokenTracker  # Ensure import
            self._tokenTracker = tokenTracker()
        else:
            self._tokenTracker = tokenTracker

        #Assert staments to check init variables
        if not os.path.exists(savePath):
            raise conversationErrors.StorageFolderNotFoundError("Invalid save path given (create a conversationArchive folder in the root directory)")

        #define and extract instance variables from .env file
        if not load_dotenv():
            raise conversationErrors.InvalidEnvError("Invalid .env file")
        self._usingUmichApi = os.getenv("USING_UMICH_API").lower() in ('true', '1', 't')

        #If the client requires the umich API to be used, access it that way. Otherwise, open the standard openAI API
        if self._usingUmichApi:
            logging.info(f"Using the umich API for {conversationName}")
            self._client = AzureOpenAI(
                api_version= os.getenv("UMICH_API_VERSION"), 
                azure_endpoint=os.getenv("UMICH_API_ENDPOINT"), 
                organization = os.getenv("UMICH_API_SHORTCODE"), 
                api_key = os.getenv("UMICH_API_KEY")) 
        else:
            logging.info(f"Using the standard openAI API for {conversationName}")
            self._client = OpenAI()

        #Clear the temp conversation save file
        with open(self._tempFilePath, "w") as file:
            file.write("")


    #PUBLIC MUTATOR FUNCTIONS--------------------------------------------

    #Main function for continuing the conversation
    def contConversation(self, newMessage: str, imagePath: str = "") -> str:
        timestamp = getTimeStamp() #get timestamp
        message = encodeMessageInternal(newMessage, timestamp, "user", "LLM", image = imagePath) #package message
        outputMessage = self.contConversationDict(message)
        return outputMessage.get("content")

    #Main function for continuing the conversation using a message dict object (more control)
    def contConversationDict(self, newMessage: dict) -> dict:
        startTime = time.time() #start timer
        self.insertMessageDict(newMessage) #Add new message
        outMessage = self.turnoverConversationDict()
        self._flattenTime(startTime) #Flatten time if needed
        return outMessage
    
    #Get a response from the LLM and store it without a human input
    def turnoverConversationDict(self) -> dict:
        #Get the last message from storage
        lastMessage = self._conversationInternal[-1]
        # if lastMessage.get("role") != "user": #REMOVED THIS ERROR CHECK TO SAVE DATA
        #     raise conversationErrors.ImproperMessageStructError("Last message in conversation is not a user message")
        iterations = 0

        #Recursievely try to make a request to the LLM
        iterations = 0
        while True:
            iterations += 1
            try:
                outputMessageText = self._makeRequest() #Make request to chat model
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

    #Insert a message into the conversation variable and file
    def insertMessage(self, newMessage: str, role: str, imagePath: str = "", note: str = ""):
        assert role in ("user", "assistant", "system"), "Invalid role given"
        timestamp = getTimeStamp() #get timestamp
        message = encodeMessageInternal(newMessage, timestamp, role, "LLM", image = imagePath, note = note)
        self.insertMessageDict(message)

    #Insert a message into the conversation variable and file
    def insertMessageDict(self, newMessage: dict):
        self._checkMessageDict(newMessage) #Check invariant
        
        content = newMessage.get("content")
        role = newMessage.get("role")
        imagePath = newMessage.get("image_path")

        self._conversation.append(encodeMessage(content, role, imagePath)) #Append message in OpenAI conversation storage
        self._conversationInternal.append(newMessage) #Append new message into internal storage
        self._updateSave() #Update conversation File

    #Make a permanent save for the current conversation
    def makeConversationSave(self, permFilePath: str = None):
        if permFilePath is None:
            permFilePath = self._savePath
        permFilePath = permFilePath + "/" + self._conversationName + self._idNumber + ".json" #generate perm storage name
        with open(permFilePath, "w") as file: #save the file
            json.dump(self._conversationInternal, file, indent = 4)

    def cleanOutImages(self):
        self._conversation = removeImgInConv(self._conversation)
        for message in self._conversationInternal:
            message["image_path"] = ""

    def makeTempMessage(self, newMessage: str, imagePath: str = "") -> str:
        timestamp = getTimeStamp()
        message = encodeMessageInternal(newMessage, timestamp, "user", "LLM", image = imagePath) #package message
        outputMessage = self.makeTempMessageDict(message)
        return outputMessage.get("content")

    # Using the history of the conversation, make a request to the LLM and return the response
    # DOES NOT RECORD ANY CHANGES TO THE CONVERSATION HISTORY
    def makeTempMessageDict(self, newMessage: dict) -> str:
        self._checkMessageDict(newMessage) #Check invariant
        
        #Unpack Message
        content = newMessage.get("content")
        role = newMessage.get("role")
        imagePath = newMessage.get("image_path")
        conversation_copy = self._conversation

        #Make a copy of the conversation and add the new message to it
        conversation_copy.append(encodeMessage(content, role, imagePath))
        conversation_copy = self._prepPrompts() + conversation_copy

        #Make a request to the LLM using the new conversation
        iterations = 0
        while True:
            iterations += 1
            try:
                outputMessageText = self._makeRequest(tempConversation = conversation_copy)
                break
            except conversationErrors.slowDownError as e:
                logging.warning(f"Slow down error caught, waiting {10*iterations} seconds before trying again")
                time.sleep(10*iterations); #wait 10 seconds before trying again
            if iterations > 6:
                raise conversationErrors.slowDownError("Too many slow down errors")

        #Repack the message into the correct format
        lastMessage = self._conversationInternal[-1]
        timestamp = getTimeStamp() #get timestamp
        assistantType = lastMessage.get("assistant_type")
        outputMessage = encodeMessageInternal(outputMessageText, timestamp, "assistant", assistantType)

        return outputMessage #return message

    #PUBLIC ACCESSOR FUNCTIONS--------------------------------------------
    def getConversation(self) -> list[dict]:
        return self._conversationInternal
    
    #Get the conversation history as a single string
    def getConversationStr(self) -> str:
        output = ""
        for message in self._conversationInternal:
            output = output + message.get("role")
            output = output + "> "
            output = output + message.get("content") + "\n"
        return output

    def getPrompts(self) -> list[str]:
        return self._prompts
    
    #PRIVATE HELPER FUNCTIONS---------------------------------------------

    #Makes a request to the LLM using either the defualt conversation and model or given new conversation and model
    #INPUT CONVERSATION IN CHATGPT FORM
    def _makeRequest(self, tempConversation: list[dict] = None, model: str = None) -> str:
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

        startTime = time.time() #start timer

        output = self._client.chat.completions.create(model = model, messages = tempConversation).choices[0].message.content #request completion
        # output = "omg wow the LLM talked" #yummy debug statement

        duration = time.time() - startTime #end timer
        duration_str = f"{duration:.2f} seconds" #convert duration to string
        self._tokenTracker.addTokenHistory(output, model) #add tokens to history
        logging.info(f"response received in {duration_str} with {self._tokenTracker.getTokensLastMinute(model)} tokens in history: " + output) #log response and time
        
        return output #return message content
            
    #Append message and potential image file to .txt file
    def _updateSave(self):
        with open(self._tempFilePath, "w") as file:
            json.dump(self._conversationInternal, file, indent = 4)

    #takes the prompts in given to it (defaults to propmts stored in class instance) and returns a set of messages ready to use
    def _prepPrompts(self, prompts: list[str] = None) -> list[dict]:
        #if the list of prompts defaults, use the prompts defined in the class instance
        if prompts is None:
            prompts = self._prompts

        #make a messages array and encode all the prompts as system messages into it
        messages = []
        for prompt in prompts:
            messages.append(encodeMessage(prompt, "system"))

        return messages
    

    #Runs some standard checks on the message data structs being passed around to catch issues early
    def _checkMessageDict(self, message: dict):
        #Check that the message has the right keys
        for key in ("content", "timestamp", "role", "assistant_type", "image_path", "note"):
            if not isinstance(message.get(key), str):
                raise conversationErrors.ImproperMessageStructError("Message is missing key: " + key)

        #Check that the message has the right values
        if not message.get("role") in ("user", "assistant", "system", "caption"):
            raise conversationErrors.ImproperMessageStructError("Invalid role given")
        if not message.get("assistant_type") in ("LLM", "human", "controller"):
            raise conversationErrors.ImproperMessageStructError(message.get("assistant_type") + " is not a valid assistant type")

    #Given the start time of the request, this function will flatten the time to be within a certain range of the goal time 
    def _flattenTime(self, startTime: float, noise = 4) -> str:
        timeElapsed = time.time() - startTime
        targetWait = random.uniform(self._timeFlattening - noise, self._timeFlattening + noise)
        
        #Check to see if function needs to be waited
        if timeElapsed < targetWait and self._timeFlattening > 0:
            logging.info(f"Flattening time by {targetWait - timeElapsed} seconds")
            time.sleep(targetWait - timeElapsed)