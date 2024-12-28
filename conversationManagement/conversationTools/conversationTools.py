import base64 #used to turn image files into useable data for the api
from datetime import datetime #used to retrieve date and time for file name
from openai import OpenAI #openai api
import logging #logging for errors and whatnot
from io import StringIO #used for in-memory logging for later file storage

#Encode a message, role, and potential image into a dictionary object
def encodeMessage(textMessage: str, role: str, imagePath: str = ""):
    if len(imagePath) != 0:
        imageData = decodeImage(imagePath)
        return {"role": role, "content":[{"type":"text", "text": textMessage}, {"type":"image_url", "image_url":{"url":f"data:image/jpeg;base64,{imageData}"}}]}
    else:
        return {"role": role,"content":[{"type":"text", "text": textMessage}]}

#open an image using the provided path and convert it into base64
def decodeImage(imagePath: str) -> str:
    with open(imagePath, "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')

#Encode a message used in internal conversation storage   
def encodeMessageInternal(textMessage: str, timestamp: str, role: str, assistantType: str, image: str = "", note: str = "") -> dict:
    Message = {
    "content": textMessage,
    "timestamp": timestamp,
    "role": role,
    "image_path": image,
    "assistant_type": assistantType,
    "note": note
    }
    return Message

#Method that splits a text file into a string array, splitting by some marker (removs the marker)
def splitFileByMarker(filename: str, marker: str) -> list[str]:
    # Read the entire file content
    with open(filename, 'r') as file:
        content = file.read()
    
    # Split the content by the marker
    split_content = content.split(marker)
    
    # Add the marker back to each entry and remove any empty entries
    split_content = [entry.strip() for entry in split_content if entry.strip()]
    
    return split_content

#Method that removes any images from a conversation formatted with the openAI format
def removeImgInConv(conversation: list[dict]) -> list[dict]:
    new_conversation = [] #init new conversation

    for message in conversation:
        role = message.get("role") #get the role of the message

        #get the text content of the message
        for part in message.get("content", []):
            if part.get("type") == "text":
                message_content = part.get("text")
        
        #append the message with the tex only to the new conversation
        new_conversation.append(encodeMessage(message_content, role))
    return new_conversation

#Get a standard formatting for the timestamp
def getTimeStamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp

#creates an 8-digit ID number based on when the documet was saved
def makeID() -> str:
    return datetime.now().strftime("%m%d")+"-"+datetime.now().strftime("%H%M")

#Use the client to make a request to make a request to the chat model 
#that extracts image features
def extract_features(client: OpenAI, model: str, image_path: str) -> str:
    # Define the vision prompt
    vision_prompt = (
        "Please analyze the image and identify abstract objects. "
        "Do NOT mention literal objects like cars, trees, or people. "
        "Instead, describe abstract elements such as lines, shapes, clusters and how they are positioned with respect to each other etc."
    )

    #Create the message
    encoded_prompt = encodeMessage(vision_prompt, "system")
    encoded_image = encodeMessage("", "user", image_path)

    # Send the request using the OpenAI client
    response = client.chat.completions.create(
        model=model,
        messages=[encoded_prompt, encoded_image]
    )

    return response.choices[0].message.content.strip()

# Function that preforms all of the logging commands we use regularly
# The creation of conversation objects works without a call to this function but this enables
# A more advanced logging system. No call to this function results in 
# a logger that default prints to the terminal
def init_logging(console_level = logging.WARNING, file_level = logging.INFO):
    logger = logging.getLogger("main")
    logger.setLevel(console_level)

    #Console handler init
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    #In-memory handler init (used for files)
    log_stream = StringIO()
    memory_handler = logging.StreamHandler(log_stream)
    memory_handler.setLevel(file_level)
    logger.addHandler(memory_handler)
