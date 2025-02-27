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

# Track connected clients
connected_users = set()  # Stores WebSocket connections for Users
connected_mentors = set()  # Stores WebSocket connections for Mentors

# Initialize a grammar correction conversation using standardConversation
grammar_correction_agent = standardConversation(
    model="gpt-4o",
    prompts=["You are a grammar correction assistant. Refine the grammar of the following message while keeping the tone and intent unchanged. Your message should be exactly like mine but without any grammar mistakes. If I say something completely nonesense, then don't change it."],
    conversationName="grammar_correction",
    savePath="conversationArchive"
)

# Add this line after initializing conversations
messages = {os.path.basename(image): [] for image in images}

def save_messages_to_json(image_name):
    global session_dir, messages
    file_path = os.path.join(session_dir, f"{image_name}.json")
    with open(file_path, 'w') as file:
        json.dump(messages[image_name], file, indent=4)
    print(f"Conversation for {image_name} saved to {file_path}")

# Helper function for broadcasting messages
async def broadcast(message, recipients):
    """Broadcast a message to a set of WebSocket recipients."""
    disconnected = set()
    for recipient in recipients:
        try:
            await recipient.send(json.dumps(message))
        except websockets.ConnectionClosed:
            disconnected.add(recipient)
    recipients.difference_update(disconnected)

# Helper function for grammar correction
def correct_grammar(message):
    """
    Correct grammar in the given message. Replace this with a real grammar correction model or API call.
    """
    # Example grammar correction logic (Replace with an actual implementation)
    corrected_message = message.capitalize()  # Capitalize the first letter as an example
    if not corrected_message.endswith("."):
        corrected_message += "."  # Ensure the message ends with a period
    return corrected_message

# WebSocket handlers
async def user_handler(websocket):
    """WebSocket Server for User."""
    global current_image_index, current_image, current_conversation
    connected_users.add(websocket)
    print("User connected.")

    try:
        while True:
            # Receive message from the user
            message = await websocket.recv()
            print(f"Message from user: {message}")
            data = json.loads(message)
            command = data.get("command", "")
            user_message = data.get("message", "")
            caption = data.get("caption", "")

            if command == "save_and_reset":
                direction = data.get("direction", "next")

                save_messages_to_json(os.path.basename(current_image))

                if direction == "next":
                    current_image_index = (current_image_index + 1) % len(images)
                elif direction == "previous":
                    current_image_index = (current_image_index - 1 + len(images)) % len(images)

                # Update to the next image and corresponding conversation
                current_image = images[current_image_index]
                current_conversation = conversations[os.path.basename(current_image)]

                # Notify mentors of the new image index
                await broadcast({
                    "status": "image_update",
                    "imageIndex": current_image_index
                }, connected_mentors)

            elif user_message:

                # Append user message to messages list
                messages[os.path.basename(current_image)].append({
                    "role": "user",
                    "message": user_message,
                    "timestamp": str(datetime.now())
                })
                
                # Broadcast the user's message to mentors
                await broadcast({
                    "role": "user",
                    "message": user_message,
                    "timestamp": str(datetime.now())
                }, connected_mentors)

            elif caption:
                # Prepend "SUBMITTED CAPTION: " to the caption
                full_caption = f"SUBMITTED CAPTION: {caption}"

                # Append caption to messages list as a user message
                messages[os.path.basename(current_image)].append({
                    "role": "user",
                    "message": full_caption,
                    "timestamp": str(datetime.now())
                })
                
                # Broadcast the caption to mentors as a user message
                await broadcast({
                    "role": "user",
                    "message": full_caption,
                    "timestamp": str(datetime.now())
                }, connected_mentors)

    except websockets.ConnectionClosed:
        print("User disconnected.")
    finally:
        connected_users.discard(websocket)

async def mentor_handler(websocket):
    global current_image, current_conversation
    connected_mentors.add(websocket)
    print("Mentor connected.")

    try:
        await websocket.send(json.dumps({"status": "image_update", "imageIndex": current_image_index}))

        while True:
            message = await websocket.recv()
            print(f"Message from mentor: {message}")
            data = json.loads(message)
            mentor_message = data.get("message", "")

            # Use the grammar correction agent with correct function call
            corrected_message = grammar_correction_agent.contConversation(mentor_message)

            # Append mentor message and corrected message to messages list
            messages[os.path.basename(current_image)].append({
                "role": "mentor",
                "message": mentor_message,
                "timestamp": str(datetime.now())
            })
            messages[os.path.basename(current_image)].append({
                "role": "grammarcorrection",
                "message": corrected_message,
                "timestamp": str(datetime.now())
            })

            # Broadcast the corrected message to users
            await broadcast({
                "role": "mentor",
                "message": corrected_message,
                "timestamp": str(datetime.now())
            }, connected_users)

            # Send the corrected message back to the mentor
            await websocket.send(json.dumps({
                "role": "grammarcorrection",
                "message": corrected_message,
                "timestamp": str(datetime.now())
            }))

    except websockets.ConnectionClosed:
        print("Mentor disconnected.")
    finally:
        connected_mentors.discard(websocket)

# Start the WebSocket server
async def main():
    user_server = await websockets.serve(user_handler, "localhost", 8765, ping_interval=None)
    mentor_server = await websockets.serve(mentor_handler, "localhost", 8766, ping_interval=None)

    # user_server = await websockets.serve(user_handler, "0.0.0.0", 8765, ping_interval=None)
    # mentor_server = await websockets.serve(mentor_handler, "0.0.0.0", 8766, ping_interval=None)

    # user_server = await websockets.serve(user_handler, "0.0.0.0", 8765)
    # mentor_server = await websockets.serve(mentor_handler, "0.0.0.0", 8766)

    print("WebSocket servers started.")
    await asyncio.gather(user_server.wait_closed(), mentor_server.wait_closed())

if __name__ == "__main__":
    asyncio.run(main())