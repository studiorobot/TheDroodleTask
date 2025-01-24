import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..'))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

# Prompt for session name
session_name = input("Enter the session name: ").strip()
if not session_name:
    raise ValueError("Session name cannot be empty.")

# Create session directory
session_dir = os.path.join("pilotStudies", session_name)
os.makedirs(session_dir, exist_ok=True)

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from conversationManagement.modularConversation.modularConversation import modularConversation #import standard conversation class
from conversationManagement.conversationTools.conversationTools import splitFileByMarker #import file splitter
import asyncio #used to run async functions
import websockets #used to create a websocket connection
import json #used to encode and decode json messages
from datetime import datetime #used to retrieve date and time for file name
import logging #used to log messages


# Define the specific images you want to use from the directory
images = ["droodleExamples/droodleExample.jpg", "droodleExamples/droodleExample2.jpg", "droodleExamples/droodleExample3.jpg", "droodleExamples/droodleExample4.jpg"]

for img in images:
    if not os.path.isfile(img):
        print(f"File not found: {img}")
    else:
        print(f"File found: {img}")

logging.basicConfig(level=logging.INFO) #config logging
load_dotenv() #load the .env file

# Initialize a conversation instance for each selected image
conversations = {}
for image_path in images:
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
    
    # Use only the filename as the identifier for each conversation
    image_name = os.path.basename(image_path)  # Extract the filename from the path
    conversations[image_name] = modularConversation("gpt-4o", constantPrompt, modularPrompt, controlPrompts, image_name)

# Global variables to keep track of the current image and conversation instance
current_image_index = 0
current_image = images[current_image_index]
# image_path = os.path.join(IMAGE_DIRECTORY, current_image)
image_path = current_image
# current_conversation = conversations[current_image]
current_conversation = conversations[os.path.basename(current_image)]

def save_conversation_to_session():
    session_image_dir = os.path.join(session_dir, os.path.basename(current_image))
    os.makedirs(session_image_dir, exist_ok=True)
    current_conversation.makeConversationSave(session_image_dir)
    logging.info(f"Conversation for {current_image} saved in session directory.")

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

            # # Handle the "save_and_reset" command from the frontend
            # if command == "save_and_reset":
            #     save_conversation_to_session()

            #     # Save the current conversation
            #     current_conversation.makeConversationSave()
            #     print(f"\n[red]System> Conversation for {current_image} saved.[/red]")

            #     # Update to the next image and corresponding conversation
            #     current_image_index = (current_image_index + 1) % len(images)  # Cycle to the next image
            #     current_image = images[current_image_index]
            #     current_conversation = conversations[os.path.basename(current_image)]

            #     initial_message = "Hello! I’m your AI guide for building a doodle caption. I’m designed to ask you questions and guide your reasoning but if you want to take control of your own creative process, I’ll be happy to help wherever possible."
            #     current_conversation.insertMessage(initial_message, "assistant")

            #     # Notify the frontend about the image switch and reset
            #     await websocket.send(json.dumps({
            #         "status": "conversation_reset",
            #         "image": current_image
            #     }))
            #     continue

            # Handle the "save_and_reset" command from the frontend
            if command == "save_and_reset":
                # Save the current conversation to the session folder
                save_conversation_to_session()

                # Save the current conversation globally
                current_conversation.makeConversationSave()
                logging.info(f"Conversation for {current_image} saved globally.")

                # Update to the next image and corresponding conversation
                current_image_index = (current_image_index + 1) % len(images)  # Cycle to the next image
                current_image = images[current_image_index]
                current_conversation = conversations[os.path.basename(current_image)]
                logging.info(f"Switched to image: {current_image}")

                # Insert the initial message if not already present
                initial_message = "Hello! I’m your AI guide for building a doodle caption. I’m designed to ask you questions and guide your reasoning but if you want to take control of your own creative process, I’ll be happy to help wherever possible."
                if not any(msg['content'] == initial_message for msg in current_conversation._conversationInternal):
                    current_conversation.insertMessage(initial_message, "assistant")

                # Notify the frontend about the image switch and reset
                await websocket.send(json.dumps({
                    "status": "conversation_reset",
                    "image": current_image
                }))
                continue

            # Handle the "save_caption" command from the frontend
            if command == "save_caption":
                caption = data.get("caption", "").strip()
                if caption:
                    # Insert the caption into the conversation
                    current_conversation.insertMessageDict({
                        "content": caption,
                        "timestamp": str(datetime.now()),
                        "role": "caption",  # Custom role for final captions
                        "image_path": current_image,
                        "assistant_type": "LLM",
                        "note": "Official Caption"
                    })

                    # Save the updated conversation
                    save_conversation_to_session()
                    current_conversation.makeConversationSave()
                    logging.info(f"Caption for {current_image} saved: {caption}")

                    # Notify the frontend about the successful save
                    await websocket.send(json.dumps({
                        "status": "caption_saved",
                        "message": "Caption saved successfully."
                    }))
                else:
                    # Handle empty caption case
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": "Caption cannot be empty."
                    }))
                continue

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

                # elif userInput.startswith("/switch_image"):
                #     # Manually switch to a new image conversation if requested
                #     current_image_index = data["switch_image"]
                #     current_image = images[current_image_index]
                #     current_conversation = conversations[os.path.basename(current_image)]
                #     imagePath = current_image  # Update imagePath to the new current image
                    
                #     # Notify the frontend about the image switch
                #     await websocket.send(json.dumps({
                #         "status": "image_switched",
                #         "image": current_image
                #     }))
                #     continue

                # elif userInput.startswith("/switch_image"):
                #     # Manually switch to a new image conversation if requested
                #     new_index = data.get("switch_image")  # Retrieve the new index from the frontend
                #     if new_index is not None and 0 <= new_index < len(images):  # Validate the new index
                #         current_image_index = new_index
                #         current_image = images[current_image_index]  # Update the current image
                #         current_conversation = conversations[os.path.basename(current_image)]  # Update the conversation
                #         logging.info(f"Switched to image: {current_image}, Index: {current_image_index}")
                        
                #         # Notify the frontend about the image switch
                #         await websocket.send(json.dumps({
                #             "status": "image_switched",
                #             "image": current_image
                #         }))
                #     else:
                #         logging.warning(f"Invalid switch_image index: {new_index}")
                #     continue
                
                # elif userInput.startswith("/switch_image"):
                #     new_index = data["switch_image"]
                #     current_image_index = new_index
                #     current_image = images[current_image_index]
                #     # current_conversation = conversations[os.path.basename(current_image)]
                #     current_conversation = modularConversation(  # Reinitialize conversation
                #         "gpt-4o",
                #         constantPrompt,
                #         modularPrompt,
                #         controlPrompts,
                #         os.path.basename(current_image)
                #     )
                #     logging.info(f"Switched to image: {current_image}, Index: {current_image_index}")
                    
                #     # Send acknowledgment to the frontend
                #     await websocket.send(json.dumps({
                #         "status": "image_switched",
                #         "image": current_image,
                #         "index": current_image_index
                #     }))

                elif userInput.startswith("/switch_image"):
                    new_index = data.get("switch_image")
                    if new_index is not None and 0 <= new_index < len(images):  # Validate index
                        current_image_index = new_index
                        current_image = images[current_image_index]
                        # current_conversation = conversations[os.path.basename(current_image)]  # Retrieve existing conversation
                        current_conversation = modularConversation(  # Reinitialize conversation
                            "gpt-4o",
                            constantPrompt,
                            modularPrompt,
                            controlPrompts,
                            os.path.basename(current_image)
                        )
                        logging.info(f"Switched to image: {current_image}, Index: {current_image_index}")
                        
                        # Notify the frontend about the image switch
                        await websocket.send(json.dumps({
                            "status": "image_switched",
                            "image": current_image,
                            "index": current_image_index
                        }))
                    else:
                        logging.warning(f"Invalid switch_image index: {new_index}")
                        await websocket.send(json.dumps({
                            "status": "error",
                            "message": "Invalid image index."
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

            save_conversation_to_session()

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