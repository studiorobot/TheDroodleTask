from openai import OpenAI #GPT resources
from openai import AzureOpenAI #umich GPT access point
import os #Used to manipulate paths and pull files
from dotenv import load_dotenv #used to pull api key from .env file
from rich import print #update the print function to include more colors
from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from datetime import datetime #used to retrieve date and time for file name

from conversationTools import encodeMessage #message encoder

class standardConversation:

    def __init__(self, model: str, prompts: list[str], conversationName: str, savePath: str = 'conversationArchive'):
        #define instance variables from function call
        self._model = model
        self._prompts = prompts
        self._conversationName = conversationName
        self._savePath = savePath
        self._tempFilePath = "./" + savePath + "/" + conversationName + "LastConversation.txt"
        self._conversation = [] #important conversation variable

        #Assert staments to check init variables
        assert os.path.exists(savePath), "Invalid path given"

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


    #HELPER FUNCTIONS--------------------------------------------------
        
    #Append message and potential image file to .txt file
    def _saveMessage(self, message: str, roleName: str, imagePath: str = ""):
        with open(self._tempFilePath, "a") as file:
            if len(imagePath) != 0:
                file.write("IMAGE INSERTED FROM: "+imagePath+"\n")
            file.write(roleName+"> "+message+"\n\n")

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
        
    #PUBLIC MUTATOR FUNCTIONS--------------------------------------------

    #Main function for continuing the conversation
    def contConversation(self, newMessage: str, imagePath: str = "") -> str:
        self.insertMessage(newMessage, "user", imagePath) #Add new text and possible image message to history
        outputMessage = self.makeRequest() #Make request to chat model
        self.insertMessage(outputMessage, "assistant") #Add assistant message to history
        return outputMessage #return chat response

    #Insert a message into the conversation variable and file
    def insertMessage(self, newMessage: str, role: str, imagePath: str = "", altRoleName: str = None):
        assert role in ("user", "assistant", "system"), "Invalid role given"

        #Set the alternate role name to the given name or the given role and capitalize the first letter
        if altRoleName is None:
            altRoleName = role
        altRoleName = altRoleName[0].upper() + altRoleName[1:]

        self._conversation.append(encodeMessage(newMessage, role, imagePath)) #Add message to conversation File
        self._saveMessage(newMessage, altRoleName, imagePath) #Note message in conversation variable
        
    #Make a permanent save for the current conversation
    def makeConversationSave(self):
        idNumber = datetime.now().strftime("%m%d")+"-"+datetime.now().strftime("%H%M") #creates an 8-digit ID number based on when the documet was saved
        permFilePath = self._savePath + "/" + self._conversationName + idNumber + ".txt"
        with open(permFilePath, "w") as newFile:
            with open(self._tempFilePath, "r") as file:
                newFile.write(file.read()) #Saves data from the temp file into the new file


    #PUBLIC ACCESSOR FUNCTIONS--------------------------------------------
    def getConversation(self) -> list[dict]:
        return self._conversation

    def getPrompts(self) -> list[str]:
        return self._prompts
    
    def makeRequest(self, tempConversation: list[dict] = None, model: str = None) -> str:
        #If conversation is allowed to default, use the conversation in the class instance and put the intial prompts at the start
        if tempConversation is None:
            tempConversation = self._prepPrompts() + self._conversation

        #if model is allowed to default, use the model given in class init
        if model is None:
            model = self._model
        
        # print("\n\nrequest made using:" + str(tempConversation)+"\n\n") #delicious delicios debugging statement
        output = self._client.chat.completions.create(model = model, messages = tempConversation) #request completion
        return output.choices[0].message.content #return message content
        
        
        # return "omg wow the LLM talked" #yummy debug statement