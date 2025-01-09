import asyncio
import websockets
import json

async def connect_to_server():
    # Replace <your-laptop-ip> with the IP address of the laptop running the backend
    # uri = "ws://<your-laptop-ip>:8767"
    uri = "ws://35.3.242.202:8767"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to the user interface. Waiting for messages...\n")

            while True:
                try:
                    # Wait for a message from the user
                    user_message = await websocket.recv()
                    data = json.loads(user_message)
                    user_text = data.get("message", "[No message received]")
                    timestamp = data.get("timestamp", "[No timestamp]")

                    # Display the user's message
                    print(f"[User at {timestamp}]: {user_text}")

                    # Prompt for a reply
                    reply = input("Your reply: ")

                    # Send the reply back to the backend
                    response = {
                        "message": reply,
                        "timestamp": timestamp
                    }
                    await websocket.send(json.dumps(response))
                    print("Reply sent!\n")

                except websockets.ConnectionClosed:
                    print("Connection to the user interface was closed.")
                    break

    except Exception as e:
        print(f"Error: {e}")

asyncio.run(connect_to_server())