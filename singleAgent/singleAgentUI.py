import os #Used to manipulate paths and pull files
from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from standardConversation import standardConversation #import standard conversation class
from controlledConversation import controlledConversation #import the controlled conversation class
import asyncio #used to run async functions
import websockets #used to create a websocket connection
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
        userInput = prompt("\nUser> ")
        if os.path.exists(userInput):
            return userInput

# #Continuously prompt the user to talk to the chatbot, relay and store the responses
# while True:
#     imagePath = "" #sets up image path variable
#     userInput = prompt("\nUser> ")

#     #Catch any commands
#     if userInput[0:1] == "/":
#         #Exit command, exits the chat without saving
#         if userInput[1:] == "exit":
#             print("\n[red]System> Exiting chat[/red]")
#             break
#         #Insert Image command, inserts image into next message
#         elif userInput[1:] == "insertImage":
#              imagePath = promptImage()
#         #Save command, saves the full chat file permanently and exits the chat
#         elif userInput[1:] == "save":
#             conv.makeConversationSave()
#             print("\n[red]System> Saving and exiting chat[/red]")
#             break
#         #Insert System Command, inserts new system message to redirect the chat LLM
#         elif userInput[1:] == "insertSystem":
#             print("\n[red]System> Input system message[/red]")
#             insert = prompt("\nUser> ")
#             conv.insertMessage(insert, "system", altRoleName="systemInsert")
#         #Command not recognized
#         else:
#             print("\n[red]System> Command Not Recognized[/red]")
#         continue

#     #if there is an image, put it into the contConversation call. Otherwise, call contConversation normally
#     if len(imagePath) != 0:
#         output = conv.contConversation(userInput, imagePath)
#         imagePath = ""
#     else:          
#         output = conv.contConversation(userInput)
#     print("\n[cyan]Assistant> "+output+"[/cyan]")


# WebSocket handler
async def handler(websocket, path):
    imagePath = ""  # Set up image path variable

    while True:
        try:
            # Receive message from the frontend via WebSocket
            message = await websocket.recv()  # Get user input from React
            data = json.loads(message)
            userInput = data.get("message", "")
            imagePath = data.get("imagePath", "")

            # Handle commands
            if userInput.startswith("/"):
                if userInput[1:] == "exit":
                    print("\n[red]System> Exiting chat[/red]")
                    response = {
                        "role": "system",
                        "message": "Exiting chat",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    break

                elif userInput[1:] == "insertImage":
                    imagePath = await promptImage(websocket)

                elif userInput[1:] == "save":
                    conv.makeConversationSave()
                    print("\n[red]System> Saving and exiting chat[/red]")
                    response = {
                        "role": "system",
                        "message": "Conversation saved and exiting chat",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    break

                elif userInput[1:] == "insertSystem":
                    response = {
                        "role": "system",
                        "message": "Insert system message",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    insert = await websocket.recv()  # Receive the system message
                    conv.insertMessage(insert, "system", altRoleName="systemInsert")
                    continue

                else:
                    response = {
                        "role": "system",
                        "message": "Command not recognized",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    continue

            # Handle the conversation flow
            if len(imagePath) != 0:
                output = conv.contConversation(userInput, imagePath)
                imagePath = ""
            else:
                output = conv.contConversation(userInput)

            # Create response with metadata (index, role, timestamp)
            response = {
                "index": 0,  # Adjust index if needed
                "role": "assistant",
                "message": output,
                "timestamp": str(datetime.now())
            }

            # Send the assistant's response back to the frontend
            await websocket.send(json.dumps(response))

        except websockets.ConnectionClosed:
            break


# Prompt for image path via WebSocket
async def promptImage(websocket) -> str:
    while True:
        response = {
            "role": "system",
            "message": "Input image path",
            "timestamp": str(datetime.now())
        }
        await websocket.send(json.dumps(response))  # Ask the frontend to send an image path
        userInput = await websocket.recv()  # Get image path from React
        if os.path.exists(userInput):
            return userInput


# Start the WebSocket server
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run WebSocket server forever

if __name__ == "__main__":
    asyncio.run(main())