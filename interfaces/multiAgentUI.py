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
from argparse import ArgumentParser

# Define the specific images you want to use from the directory
images = ["droodleExamples/droodleExample.jpg", "droodleExamples/droodleExample2.jpg", "droodleExamples/droodleExample3.jpg", "droodleExamples/droodleExample4.jpg"]

for img in images:
    if not os.path.isfile(img):
        print(f"File not found: {img}")
    else:
        print(f"File found: {img}")

hlm_histories = {os.path.basename(image): [] for image in images}  # Initialize per-image history

logging.basicConfig(level=logging.INFO) #config logging
load_dotenv() #load the .env file

# Initialize command-line argument parser
parser = ArgumentParser()
parser.add_argument("--mode", choices=["vlm", "hlm"], default="vlm", help="Select mode: vlm or hlm")
args = parser.parse_args()

# Initialize conversation instances based on mode
if args.mode == "vlm":
    conversations = {}
    for image_path in images:
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

elif args.mode == "hlm":
    grammar_prompts = [
        "Please rewrite the following message with perfect grammar. Do not change the tone, style, or meaning of the message. If there is ambiguity, leave it as it is."
    ]
    grammar_agent = standardConversation(
        model="gpt-4", prompts=grammar_prompts, conversationName="GrammarAgent"
    )

# Global variables to manage current state
current_image_index = 0
current_image = images[current_image_index]
if args.mode == "vlm":
    current_conversation = conversations[os.path.basename(current_image)]

async def handler(websocket, path):
    global current_image, current_image_index, current_conversation

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
                if args.mode == "vlm":
                    current_conversation.makeConversationSave()
                    print(f"\n[red]System> Conversation for {current_image} saved.[/red]")

                if args.mode == "hlm":
                    for image_name, history in hlm_histories.items():
                        if history:  # Only save if there are interactions for this image
                            save_path = f"conversationArchive/HLM_{image_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            os.makedirs(os.path.dirname(save_path), exist_ok=True)
                            with open(save_path, "w") as file:
                                json.dump(history, file, indent=4)
                            logging.info(f"H-LM conversation for {image_name} saved to {save_path}.")
                            hlm_histories[image_name].clear()  # Clear history for this image after saving

                current_image_index = (current_image_index + 1) % len(images)  # Cycle to the next image
                current_image = images[current_image_index]
                if args.mode == "vlm":
                    current_conversation = conversations[os.path.basename(current_image)]

                initial_message = "Hello! I’m your AI guide for building a doodle caption. I’m designed to ask you questions and guide your reasoning but if you want to take control of your own creative process, I’ll be happy to help wherever possible."
                if args.mode == "vlm":
                    current_conversation.insertMessage(initial_message, "assistant")

                await websocket.send(json.dumps({
                    "status": "conversation_reset",
                    "image": current_image
                }))
                continue

            # Process the conversation
            if args.mode == "vlm":
                output = current_conversation.contConversation(userInput, imagePath)

            elif args.mode == "hlm":
                print(f"User: {userInput}")
                human_response = input("Human Operator (type your response): ")
                output = grammar_agent.contConversation(human_response)

                hlm_histories[os.path.basename(current_image)].append({
                    "timestamp": str(datetime.now()),
                    "user_message": userInput,
                    "human_response": human_response,
                    "final_output": output,
                })

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
