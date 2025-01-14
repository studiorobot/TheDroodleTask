# import os  # Used to manipulate paths and pull files
# import sys  # Uses to access modules
# import asyncio  # Used to run async functions
# import websockets  # Used to create WebSocket connections
# import json  # Used to encode and decode JSON messages
# from datetime import datetime  # Used to retrieve date and time for file name
# import logging  # Used to log messages

# sys.path.append(os.path.abspath(".."))
# os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Set working directory

# # Global variables to keep track of WebSocket connections
# human_operator_ws = None

# # Define the specific images you want to use from the directory
# images = [
#     "droodleExamples/droodleExample.jpg",
#     "droodleExamples/droodleExample2.jpg",
#     "droodleExamples/droodleExample3.jpg",
#     "droodleExamples/droodleExample4.jpg",
# ]

# # Validate image files
# for img in images:
#     if not os.path.isfile(img):
#         print(f"File not found: {img}")
#     else:
#         print(f"File found: {img}")

# logging.basicConfig(level=logging.INFO)  # Configure logging

# # Global variables to manage current state
# current_image_index = 0
# current_image = images[current_image_index]


# async def user_handler(websocket, path):
#     """
#     Handles the connection with the user's frontend.
#     """
#     global human_operator_ws, current_image_index, current_image

#     while True:
#         try:
#             # Receive message from the user
#             message = await websocket.recv()
#             data = json.loads(message)
#             userInput = data.get("message", "")
#             command = data.get("command", "")  # Handle save and reset commands

#             if command == "save_and_reset":
#                 # Save the current conversation (placeholder logic)
#                 print(f"\n[INFO] Conversation for {current_image} saved.")

#                 # Move to the next image
#                 current_image_index = (current_image_index + 1) % len(images)
#                 current_image = images[current_image_index]

#                 # Notify the frontend about the image switch
#                 await websocket.send(json.dumps({"status": "conversation_reset", "image": current_image}))
#                 continue

#             # Forward user input to the human operator
#             if human_operator_ws:
#                 await human_operator_ws.send(json.dumps({"message": userInput, "timestamp": str(datetime.now())}))
#                 # Wait for the human operator's response
#                 human_response = await human_operator_ws.recv()
#                 response_data = json.loads(human_response)
#                 response = {
#                     "role": "assistant",
#                     "message": response_data.get("message", ""),
#                     "timestamp": response_data.get("timestamp", str(datetime.now())),
#                 }
#             else:
#                 response = {
#                     "role": "assistant",
#                     "message": "No human operator connected.",
#                     "timestamp": str(datetime.now()),
#                 }

#             # Send the response back to the user's frontend
#             await websocket.send(json.dumps(response))

#         except websockets.ConnectionClosed:
#             print("User disconnected.")
#             break


# async def human_operator_handler(websocket, path):
#     """
#     Handles the connection with the human operator's frontend.
#     """
#     global human_operator_ws
#     human_operator_ws = websocket
#     print("Human operator connected.")

#     try:
#         await asyncio.Future()  # Keep connection open indefinitely
#     except websockets.ConnectionClosed:
#         print("Human operator disconnected.")
#         human_operator_ws = None


# async def main():
#     """
#     Starts WebSocket servers for the user and human operator.
#     """
#     # User WebSocket server on port 8766
#     user_server = websockets.serve(user_handler, "localhost", 8766)

#     # Human operator WebSocket server on port 8767
#     # human_server = websockets.serve(human_operator_handler, "localhost", 8767)
#     human_server = websockets.serve(human_operator_handler, "0.0.0.0", 8767)
    
#     # Run both WebSocket servers and prevent script from exiting
#     await asyncio.gather(user_server, human_server, asyncio.Future())


# if __name__ == "__main__":
#     asyncio.run(main())

############################################################################################
############################################################################################
############################################################################################

import os  # Used to manipulate paths and pull files
import sys  # Uses to access modules
import asyncio  # Used to run async functions
import websockets  # Used to create WebSocket connections
import json  # Used to encode and decode JSON messages
from datetime import datetime  # Used to retrieve date and time for file name
import logging  # Used to log messages

sys.path.append(os.path.abspath(".."))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Set working directory

from conversationManagement.standardConversation.standardConversation import standardConversation  # Import standardConversation

# Global variables to keep track of WebSocket connections
human_operator_ws = None

# Define the specific images you want to use from the directory
images = [
    "droodleExamples/droodleExample.jpg",
    "droodleExamples/droodleExample2.jpg",
    "droodleExamples/droodleExample3.jpg",
    "droodleExamples/droodleExample4.jpg",
]

# Validate image files
for img in images:
    if not os.path.isfile(img):
        print(f"File not found: {img}")
    else:
        print(f"File found: {img}")

logging.basicConfig(level=logging.INFO)  # Configure logging

# Global variables to manage current state
current_image_index = 0
current_image = images[current_image_index]

# Initialize the OpenAI summarization agent
summarization_prompts = ["Please rewrite the following message with perfect grammar. Do not change the tone, style, or meaning of the message. If there is ambiguity in the message, leave it as it is. Focus only on correcting grammar. Do not rephrase or summarize."]
summarization_agent = standardConversation(model="gpt-4", prompts=summarization_prompts, conversationName="SummarizationAgent")


async def user_handler(websocket, path):
    """
    Handles the connection with the user's frontend.
    """
    global human_operator_ws, current_image_index, current_image

    while True:
        try:
            # Receive message from the user
            message = await websocket.recv()
            data = json.loads(message)
            userInput = data.get("message", "")
            command = data.get("command", "")  # Handle save and reset commands

            if command == "save_and_reset":
                # Save the current conversation (placeholder logic)
                print(f"\n[INFO] Conversation for {current_image} saved.")

                # Move to the next image
                current_image_index = (current_image_index + 1) % len(images)
                current_image = images[current_image_index]

                # Notify the frontend about the image switch
                await websocket.send(json.dumps({"status": "conversation_reset", "image": current_image}))
                continue

            # Forward user input to the human operator
            if human_operator_ws:
                await human_operator_ws.send(json.dumps({"message": userInput, "timestamp": str(datetime.now())}))
                # Wait for the human operator's response
                human_response = await human_operator_ws.recv()
                response_data = json.loads(human_response)
                human_message = response_data.get("message", "")

                # Pass the human operator's response through the summarization agent
                summarized_response = summarization_agent.contConversation(human_message)

                response = {
                    "role": "assistant",
                    "message": summarized_response,
                    "timestamp": str(datetime.now()),
                }
            else:
                response = {
                    "role": "assistant",
                    "message": "No human operator connected.",
                    "timestamp": str(datetime.now()),
                }

            # Send the response back to the user's frontend
            await websocket.send(json.dumps(response))

        except websockets.ConnectionClosed:
            print("User disconnected.")
            break


async def human_operator_handler(websocket, path):
    """
    Handles the connection with the human operator's frontend.
    """
    global human_operator_ws
    human_operator_ws = websocket
    print("Human operator connected.")

    try:
        await asyncio.Future()  # Keep connection open indefinitely
    except websockets.ConnectionClosed:
        print("Human operator disconnected.")
        human_operator_ws = None


async def main():
    """
    Starts WebSocket servers for the user and human operator.
    """
    # User WebSocket server on port 8766
    user_server = websockets.serve(user_handler, "localhost", 8766)

    # Human operator WebSocket server on port 8767
    human_server = websockets.serve(human_operator_handler, "0.0.0.0", 8767)
    
    # Run both WebSocket servers and prevent script from exiting
    await asyncio.gather(user_server, human_server, asyncio.Future())


if __name__ == "__main__":
    asyncio.run(main())