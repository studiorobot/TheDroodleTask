import os #Used to manipulate paths and pull files
import sys #Uses to access modules

sys.path.append(os.path.abspath('..'))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from prompt_toolkit import prompt #Used to manage inputs from the user in the chat
from dotenv import load_dotenv #used to load the .env file
from rich import print #update the print function to include more colors
from conversationManagement.standardConversation.standardConversation import standardConversation #import standard conversation class
from conversationManagement.modularConversation.controlledModularConversation import controlledModularConversation #import controlled modular conversation class
from conversationManagement.conversationTools.conversationTools import splitFileByMarker #import file splitter
from conversationManagement.featureExtraction.featureExtractor import featureExtractor #import feature extractor
import asyncio #used to run async functions
import websockets #used to create a websocket connection
import json #used to encode and decode json messages
from datetime import datetime #used to retrieve date and time for file name
from openai import OpenAI #GPT resources

# Define the specific images you want to use from the directory
images = ["droodleExamples/droodleExample.jpg", "droodleExamples/droodleExample2.jpg", "droodleExamples/droodleExample3.jpg", "droodleExamples/droodleExample4.jpg"]

for img in images:
    if not os.path.isfile(img):
        print(f"File not found: {img}")
    else:
        print(f"File found: {img}")

load_dotenv() #load the .env file
client = OpenAI() #initialize the OpenAI client
# Initialize a conversation instance for each selected image
conversations = {}
for image_path in images:
    # Initialize the featureExtractor for the image
    feature_extractor = featureExtractor("gpt-4o", image_path, client)

    try:
        # Extract the features from the image
        extracted_features = feature_extractor.extract_features(client)
        print(f"Extracted features for {image_path}: {extracted_features}")
    except Exception as e:
        print(f"Failed to extract features for {image_path}: {e}")
        extracted_features = ""

    #The below lines extract the prompt info from files and store them in the prompt list
    constantPrompt = [] #init constant prompt
    with open("prompts/modularPrompt.txt", "r") as file:
        constantPrompt.append(file.read())

    # Augment the constant prompt with the extracted features
    if extracted_features:
        constantPrompt[0] = feature_extractor.augment_constant_prompt(constantPrompt[0])
        
    modularPrompt = splitFileByMarker("prompts/modularConversationGuide.txt", "###")

    with open("prompts/modularControllerExtrapPrompt.txt", "r") as file:
        controlPrompt = file.read()
    
    # Use only the filename as the identifier for each conversation
    image_name = os.path.basename(image_path)  # Extract the filename from the path
    conversations[image_name] = controlledModularConversation("gpt-4o", constantPrompt, modularPrompt, controlPrompt, image_name)
    # conversation = controlledModularConversation(
    #     "gpt-4o", constantPrompt, modularPrompt, controlPrompt, image_name
    # )

    # Use the conversation's client for feature extraction
    # feature_extractor = featureExtractor(
    #     "gpt-4o",
    #     image_path,
    #     conversation.getClient()  # Reuse the client from the conversation instance
    # )


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
                # Save the current conversation
                current_conversation.makeConversationSave()
                print(f"\n[red]System> Conversation for {current_image} saved.[/red]")

                # Update to the next image and corresponding conversation
                current_image_index = (current_image_index + 1) % len(images)  # Cycle to the next image
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