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

from conversationManagement.conversationTools.conversationTools import encodeMessage, encodeMessageInternal #message encoders

class standardConversation:

    def __init__(self, model: str, prompts: list[str], conversationName: str, savePath: str = 'conversationArchive'):
        #define instance variables from function call
        self._model = model
        self._prompts = prompts
        self._conversationName = conversationName
        self._savePath = savePath
        self._tempFilePath = "./" + savePath + "/" + conversationName + "LastConversation.json"
        self._conversation = [] #important conversation variable for openAI
        self._conversationInternal = [] #conversation variable for our storage

        #Assert staments to check init variables
        assert os.path.exists(savePath), "Invalid path given (create a conversationArchive folder in the root directory)"

        #define and extract instance variables from .env file
        load_dotenv()
        self._usingUmichApi = os.getenv("USING_UMICH_API").lower() in ('true', '1', 't')

        #If the client requires the umich API to be used, access it that way. Otherwise, open the standard openAI API
        if self._usingUmichApi:
            self._client = AzureOpenAI(
                api_version= os.getenv("UMICH_API_VERSION"), 
                azure_endpoint=os.getenv("UMICH_API_ENDPOINT"), 
                organization = os.getenv("UMICH_API_SHORTCODE"), 
                api_key = os.getenv("UMICH_API_KEY")) 
        else:
            self._client = OpenAI()

        #Clear the temp conversation save file
        with open(self._tempFilePath, "w") as file:
            file.write("")


    #PUBLIC MUTATOR FUNCTIONS--------------------------------------------

    #**LEGACY** Main function for continuing the conversation
    def contConversation(self, newMessage: str, imagePath: str = "") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp
        message = encodeMessageInternal(newMessage, timestamp, "user", "LLM", image = imagePath) #package message
        outputMessage = self.contConversationDict(message)
        return outputMessage.get("content")

    #Main function for continuing the conversation using a message dict object
    def contConversationDict(self, newMessage: dict) -> dict:
        self.insertMessageDict(newMessage) #Add new message

        outputMessageText = self.makeRequest() #Make request to chat model
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp
        sessionNumber = newMessage.get("session_number") #get session number
        assistantType = newMessage.get("assistant_type")
        outputMessage = encodeMessageInternal(outputMessageText, timestamp, "assistant", assistantType, sessionNumber = sessionNumber) #package message

        self.insertMessageDict(outputMessage)
        return outputMessage

    #**LEGACY** Insert a message into the conversation variable and file
    def insertMessage(self, newMessage: str, role: str, imagePath: str = "", note: str = ""):
        assert role in ("user", "assistant", "system"), "Invalid role given"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp
        message = encodeMessageInternal(newMessage, timestamp, role, "LLM", image = imagePath, note = note)
        self.insertMessageDict(message)

    #Insert a message into the conversation variable and file
    def insertMessageDict(self, newMessage: dict):
        content = newMessage.get("content")
        role = newMessage.get("role")
        imagePath = newMessage.get("image_path")

        self._conversation.append(encodeMessage(content, role, imagePath)) #Append message in OpenAI conversation storage
        self._conversationInternal.append(newMessage) #Append new message into internal storage
        self._updateSave() #Update conversation File

    #Make a permanent save for the current conversation
    def makeConversationSave(self):
        idNumber = datetime.now().strftime("%m%d")+"-"+datetime.now().strftime("%H%M") #creates an 8-digit ID number based on when the documet was saved
        permFilePath = self._savePath + "/" + self._conversationName + idNumber + ".json" #generate perm storage name
        with open(permFilePath, "w") as file: #save the file
            json.dump(self._conversationInternal, file, indent = 4)


    #PUBLIC ACCESSOR FUNCTIONS--------------------------------------------
    def getConversation(self) -> list[dict]:
        return self._conversationInternal

    def getPrompts(self) -> list[str]:
        return self._prompts
    
    def makeRequest(self, tempConversation: list[dict] = None, model: str = None) -> str:
        #If conversation is allowed to default, use the conversation in the class instance and put the intial prompts at the start
        if tempConversation is None:
            tempConversation = self._prepPrompts() + self._conversation

        #if model is allowed to default, use the model given in class init
        if model is None:
            model = self._model
        
        print("\n\nrequest made using:" + str(tempConversation)+"\n\n") #delicious delicios debugging statement
        # output = self._client.chat.completions.create(model = model, messages = tempConversation) #request completion
        # return output.choices[0].message.content #return message content
        
        
        return "omg wow the LLM talked" #yummy debug statement
    
    #PRIVATE HELPER FUNCTIONS---------------------------------------------
        
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
        