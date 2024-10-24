import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..')) #Needed to find modules
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
import json #used to encode and decode json messages
from conversationManagement.elizaConversation.elizaConversation import elizaConversation
from datetime import datetime #used to retrieve date and time for file name

conv = elizaConversation("elizaTerminal") #create a conversation instance

while True:
    userInput = prompt("\nUser> ")

    #Catch any commands
    if userInput[0:1] == "/":
        #Exit command, exits the chat without saving
        if userInput[1:] == "exit":
            print("\n[red]System> Exiting chat[/red]")
            break
        #Save command, saves the full chat file permanently and exits the chat
        elif userInput[1:] == "save":
            conv.makeConversationSave()
            print("\n[red]System> Saving and exiting chat[/red]")
            break
        #Command not recognized
        else:
            print("\n[red]System> Command Not Recognized[/red]")
        continue
    else:          
        output = conv.contConversation(userInput)
    print("\n[cyan]Assistant> "+output+"[/cyan]")