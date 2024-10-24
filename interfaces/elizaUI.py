import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..')) #Needed to find modules
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
import json #used to encode and decode json messages
from conversationManagement.elizaConversation.elizaConversation import elizaConversation
from conversationManagement.conversationTools.conversationTools import encodeMessageInternal #used to encode internal message dicts
from datetime import datetime #used to retrieve date and time for file name
import asyncio #used to run async functions
import websockets #used to create a websocket connection
import json #used to encode and decode json messages

conv = elizaConversation("elizaTerminal") #create a conversation instance

# WebSocket handler
async def handler(websocket, path):
    while True:
        try:
            # Receive message from the frontend via WebSocket
            message = await websocket.recv()  # Get user input from React
            data = json.loads(message)
            userInput = data.get("message", "")

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

                else:
                    response = {
                        "role": "system",
                        "message": "Command not recognized",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    continue

            # Handle the conversation flow
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp
            userInputEncoded = encodeMessageInternal(userInput, timestamp, "user", "Eliza")
            output = conv.contConversationDict(userInputEncoded)

            # Create response with metadata (index, role, timestamp)
            response = {
                "index": 0,  # Adjust index if needed
                "role": "assistant",
                "message": output.get("content"),
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