import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..'))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from conversationManagement.modularConversation.modularConversation import modularConversation #import standard conversation class
from conversationManagement.standardConversation.standardConversation import standardConversation
from conversationManagement.conversationTools.conversationTools import splitFileByMarker #import file splitter
import asyncio #used to run async functions
import websockets #used to create a websocket connection
import json #used to encode and decode json messages
from datetime import datetime #used to retrieve date and time for file name
import logging #used to log messages


# Define the specific images you want to use from the directory
images = ["droodleExamples/droodleExample1.jpg", "droodleExamples/droodleExample2.jpg", "droodleExamples/droodleExample3.jpg", "droodleExamples/droodleExample4.jpg"]

for img in images:
    if not os.path.isfile(img):
        print(f"File not found: {img}")
    else:
        print(f"File found: {img}")

logging.basicConfig(level=logging.INFO) #config logging
load_dotenv() #load the .env file

# Prompt for session name
session_name = input("Enter the session name: ").strip()
if not session_name:
    raise ValueError("Session name cannot be empty.")

# Create session directory
session_dir = os.path.join("conversationArchive", session_name)
os.makedirs(session_dir, exist_ok=True)

# # Initialize a conversation instance for each selected image
# conversations = {}
# for image_path in images:
#     #The below lines extract the prompt info from files and store them in the prompt list
#     constantPrompt = [] #init constant prompt
#     with open("prompts/modularPrompt.txt", "r") as file:
#         constantPrompt.append(file.read())
        
#     modularPrompt = splitFileByMarker("prompts/modularConversationGuide.txt", "###")

#     controlPrompts = [] #init control prompt
#     with open("prompts/modularControllerArgumentPrompt.txt", "r") as file:
#         controlPrompts.append(file.read())
#     with open("prompts/moduleArgumentPrompt.txt", "r") as file:
#         controlPrompts.append(file.read())
    
#     # Use only the filename as the identifier for each conversation
#     image_name = os.path.basename(image_path)  # Extract the filename from the path
#     conversations[image_name] = modularConversation("gpt-4o", constantPrompt, modularPrompt, controlPrompts, image_name)

# Load the initial prompt for the agent
with open("prompts/baseline_prompt.txt", "r") as file:
    initial_prompt = file.read()

# Initialize conversations for each image
conversations = {}
for image_path in images:
    image_name = os.path.basename(image_path)  # Extract the filename
    conversations[image_name] = standardConversation(
        model="gpt-4o",
        prompts=[initial_prompt],  # StandardConversation uses a list of prompts
        conversationName=image_name,
        savePath="conversationArchive"
    )

# Global variables to keep track of the current image and conversation instance
current_image_index = 0
current_image = images[current_image_index]
# image_path = os.path.join(IMAGE_DIRECTORY, current_image)
image_path = current_image
# current_conversation = conversations[current_image]
current_conversation = conversations[os.path.basename(current_image)]


async def handler(websocket, path):
    global current_image_index, current_image, current_conversation
    while True:
        try:
            # Receive message from the frontend via WebSocket
            message = await websocket.recv()
            data = json.loads(message)
            userInput = data.get("message", "")
            command = data.get("command", "")  # New field for specific commands like "save_and_reset"
            
            # Automatically set `imagePath` based on `current_image`
            imagePath = current_image  # Always use the current image

            # Handle the "save_and_reset" command from the frontend
            if command == "save_and_reset":
                direction = data.get("direction", "next")  # Get navigation direction (default to "next")

                # Save the current conversation
                # current_conversation.makeConversationSave()
                current_conversation.makeConversationSave(permFilePath=session_dir)
                print(f"\n[red]System> Conversation for {current_image} saved.[/red]")

                # Determine next image index based on direction
                if direction == "next":
                    current_image_index = (current_image_index + 1) % len(images)  # Move forward
                elif direction == "previous":
                    current_image_index = (current_image_index - 1 + len(images)) % len(images)  # Move backward

                # Update to the next image and corresponding conversation
                # current_image_index = (current_image_index + 1) % len(images)  # Cycle to the next image
                current_image = images[current_image_index]
                current_conversation = conversations[os.path.basename(current_image)]

                initial_message = "Hello! I’m your AI guide for building a doodle caption. I’m designed to ask you questions and guide your reasoning but if you want to take control of your own creative process, I’ll be happy to help wherever possible."
                current_conversation.insertMessage(initial_message, "assistant")

                # Notify the frontend about the image switch and reset
                await websocket.send(json.dumps({
                    "status": "conversation_reset",
                    "image": current_image
                }))
                continue

            if command == "submit_caption":
                caption_text = data.get("caption", "")
                image_index = data.get("imageIndex", -1)
                
                if caption_text and 0 <= image_index < len(images):
                    image_name = os.path.basename(images[image_index])
                    conversations[image_name].insertMessage(f"User submitted caption: {caption_text}", "user")
                    print(f"Caption received for {image_name}: {caption_text}")

                    # Send confirmation back to frontend
                    await websocket.send(json.dumps({
                        "status": "caption_received",
                        "message": f"Caption for {image_name} saved."
                    }))
                else:
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": "Invalid caption or image index."
                    }))

            # Handle commands if the userInput starts with a "/"
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
                    current_conversation.makeConversationSave()
                    print("\n[red]System> Saving and exiting chat[/red]")
                    response = {
                        "role": "system",
                        "message": "Conversation saved and exiting chat",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    break

                elif userInput.startswith("/switch_image"):
                    # Manually switch to a new image conversation if requested
                    current_image_index = data["switch_image"]
                    current_image = images[current_image_index]
                    current_conversation = conversations[os.path.basename(current_image)]
                    imagePath = current_image  # Update imagePath to the new current image
                    
                    # Notify the frontend about the image switch
                    await websocket.send(json.dumps({
                        "status": "image_switched",
                        "image": current_image
                    }))
                    continue

                else:
                    response = {
                        "role": "system",
                        "message": "Command not recognized",
                        "timestamp": str(datetime.now())
                    }
                    await websocket.send(json.dumps(response))
                    continue

            # Process the conversation using the automatically set imagePath
            output = current_conversation.contConversation(userInput, imagePath)

            # Create a response with metadata (index, role, timestamp)
            response = {
                "index": current_image_index,  # Index of the current image
                "role": "assistant",
                "message": output,
                "timestamp": str(datetime.now())
            }

            # Send the assistant's response back to the frontend
            await websocket.send(json.dumps(response))

        except websockets.ConnectionClosed:
            break

# Start the WebSocket server
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run WebSocket server forever

if __name__ == "__main__":
    asyncio.run(main())