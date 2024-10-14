import os
import asyncio
import websockets
import json
import random  # For generating random numbers or letters
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables (this part remains unchanged)
load_dotenv()
isExpert = os.getenv("IS_EXPERT").lower() in ('true', '1', 't')
isControlled = os.getenv("IS_CONTROLLED").lower() in ('true', '1', 't')

# WebSocket handler with a dummy chatbot
async def handler(websocket, path):
    while True:
        try:
            # Receive message from the frontend via WebSocket
            message = await websocket.recv()
            data = json.loads(message)
            userInput = data.get("message", "")

            # Generate a dummy response (random number or letter)
            random_response = random.choice([str(random.randint(0, 100)), chr(random.randint(65, 90))])  # Random number or letter

            # Create response with metadata (index, role, timestamp)
            response = {
                "index": 0,  # Adjust index if needed
                "role": "assistant",
                "message": random_response,
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