import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..')) #Needed to find modules
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from conversationManagement.modularConversation.modularConversation import modularConversation, module #import conversation class
from conversationManagement.conversationTools.conversationTools import splitFileByMarker, encodeMessageInternal
from datetime import datetime #used to retrieve date and time for file name
import logging #used to log messages

logging.basicConfig(level=logging.INFO) #config logging
load_dotenv() #load the .env file

#The below lines extract the prompt info from files and store them in the prompt list
constantPrompt = [] #init constant prompt
with open("prompts/modularPrompt.txt", "r") as file:
    constantPrompt.append(file.read())
    
modularPrompt = splitFileByMarker("prompts/modularConversationGuide.txt", "###")

controlPrompts = [] #init control prompt 
with open("prompts/modularControllerArgumentPrompt.txt", "r") as file:
    controlPrompts.append(file.read())
with open("prompts/moduleArgumentPrompt.txt", "r") as file:
    controlPrompts.append(file.read())


#Init the conversation variable
conv = modularConversation("gpt-4o", constantPrompt, modularPrompt, controlPrompts, "terminal")

#Add the intial message
initial_message_str = "Hello! I’m your AI guide for building a doodle caption. I’m designed to ask you questions and guide your reasoning but if you want to take control of your own creative process, I’ll be happy to help wherever possible."
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp
initial_message = encodeMessageInternal(initial_message_str, timestamp, "assistant", "LLM")
conv.insertMessageDict(initial_message)
print("\n[blue]Assistant - init(N/A)> "+initial_message_str+"[/blue]")

#prompt the user to input an image path and return the path string. If image path does not exist, prompt again
def promptImage() -> str:
     while True:
        print("\n[red]System> Input image path[/red]")
        print("[red]Current working directory: "+os.getcwd()+"[/red]")
        userInput = prompt("\nUser> ")
        if os.path.exists(userInput):
            return userInput

#Continuously prompt the user to talk to the chatbot, relay and store the responses
imagePath = "" #sets up image path variable
while True:
    userInput = prompt("\nUser> ")

    #Catch any commands
    if userInput[0:1] == "/":
        #Exit command, exits the chat without saving
        if userInput[1:] == "exit":
            print("\n[red]System> Exiting chat[/red]")
            break
        #Insert Image command, inserts image into next message
        elif userInput[1:] == "insertImage":
             imagePath = promptImage()
        #Save command, saves the full chat file permanently and exits the chat
        elif userInput[1:] == "save":
            conv.makeConversationSave()
            print("\n[red]System> Saving and exiting chat[/red]")
            break
        #Insert System Command, inserts new system message to redirect the chat LLM
        elif userInput[1:] == "insertSystem":
            print("\n[red]System> Input system message[/red]")
            insert = prompt("\nUser> ")
            conv.insertMessage(insert, "system", altRoleName="systemInsert")
        #Test command, a placeholder for whatever I want 
        elif userInput[1:] == "test":
            with open("test.txt", "w") as file:
                file.write(conv.getConversationStr())
            print("\n[red]System> Made a test text file :)[/red]")
        #Command not recognized
        else:
            print("\n[red]System> Command Not Recognized[/red]")
        continue

    #if there is an image, put it into the insert. Otherwise, insert the user message in and get all possible next messages
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp
    message = encodeMessageInternal(userInput, timestamp, "user", "LLM", image = imagePath)
    if(imagePath != ""):
        imagePath = "" #reset the image path

    #Continue the conversation
    response = conv.contConversationDict(message)

    print("\n[blue]Assistant - " + conv.getState().name + "(" + str(conv.getState().value) + ")> "+response.get("content")+"[/blue]")
