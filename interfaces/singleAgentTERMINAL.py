import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..')) #Needed to find modules
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from conversationManagement.standardConversation.standardConversation import standardConversation #import standard conversation class
from conversationManagement.controlledConversation.controlledConversation import controlledConversation #import the controlled conversation class
import json #used to encode and decode json messages
from datetime import datetime #used to retrieve date and time for file name

load_dotenv() #load the .env file
isExpert = os.getenv("IS_EXPERT").lower() in ('true', '1', 't')
isControlled = os.getenv("IS_CONTROLLED").lower() in ('true', '1', 't')

#Set prompt file names, selecting for expert or non-expert, based on env
if isExpert:
    promptFile = "prompts/promptExpert.txt"
    conversationGuideFile = "prompts/conversationGuideExpert.txt"
    print("[red]System> Booting Expert LLM[/red]")
else:
    promptFile = "prompts/prompt.txt"
    conversationGuideFile = "prompts/conversationGuide.txt"
    print("[red]System> Booting Non-Expert LLM[/red]")

prompts = [] #init prompt file

#The below lines extract the prompt info from files and store them in the prompt list
with open(promptFile, "r") as file:
    prompts.append(file.read())
with open(conversationGuideFile, "r") as file:
    prompts.append(file.read())

if not isControlled:
    conv = standardConversation("gpt-4o", prompts, "singleAgent") #create a conversation instance
else:
    controllPrompts = []
    with open("prompts/controllerPrompt.txt") as file:
        controllPrompts.append(file.read())
    conv = controlledConversation("gpt-4o", "gpt-4o", prompts, controllPrompts,"singleAgent")

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
        #Command not recognized
        else:
            print("\n[red]System> Command Not Recognized[/red]")
        continue

    #if there is an image, put it into the contConversation call. Otherwise, call contConversation normally
    if len(imagePath) != 0:
        output = conv.contConversation(userInput, imagePath)
        imagePath = ""
    else:          
        output = conv.contConversation(userInput)
    print("\n[cyan]Assistant> "+output+"[/cyan]")