import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..')) #Needed to find modules
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from conversationManagement.modularConversation.modularConversation import modularConversation, module #import standard conversation class
from conversationManagement.conversationTools.conversationTools import splitFileByMarker
from datetime import datetime #used to retrieve date and time for file name

load_dotenv() #load the .env file

#Select the propt and conversationGuide Files
conversationGuideFile = "prompts/conversationGuideExpert.txt"

#The below lines extract the prompt info from files and store them in the prompt list
constantPrompt = [] #init constant prompt file
with open("prompts/promptExpert.txt", "r") as file:
    constantPrompt.append(file.read())
    
modularPrompt = splitFileByMarker("prompts/modularConversationGuide.txt", "###")

#Init the conversation variable
conv = modularConversation("gpt-4o", constantPrompt, modularPrompt, "modularConv") #create a conversation instance


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

    #if there is an image, put it into the insert. Otherwise, insert the user message in and get all possible next messages
    if len(imagePath) != 0:
        conv.insertMessage(userInput, "user", imagePath)
        imagePath = ""
    else:          
        conv.insertMessage(userInput, "user", imagePath)

    #Get Next possibilities
    possibleMessages = conv.possibleNextMessages()
    possibleModules = conv.allPossibleStates()
    
    #print each module's response
    for i in range(len(possibleModules)):
        possibleMessage = possibleMessages[i]
        indevModule = possibleModules[i]
        print("[pink]Assistant - " + indevModule.name + "(" + str(indevModule.value) + ")> "+possibleMessage.get("content")+"[/pink]")

    #Ask for module selection
    print("\n[red]System> Select a Module (a number 0 - 9)[/red]")
    userInput = prompt("\nUser> ")
    toModule = module(int(userInput))

    #Swtich the conversation mode and continue
    conv.switchState(toModule)
    response = conv.turnoverConversationDict()

    print("\n[blue]Assistant - " + toModule.name + "(" + str(toModule.value) + ")> "+response.get("content")+"[/blue]")
