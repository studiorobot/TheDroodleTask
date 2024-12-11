import base64 #used to turn image files into useable data for the api
from datetime import datetime #used to retrieve date and time for file name

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
def encodeMessageInternal(textMessage: str, timestamp: str, role: str, assistantType: str, sessionNumber: int = -1, image: str = "", note: str = "") -> dict:
    Message = {
    "content": textMessage,
    "timestamp": timestamp,
    "role": role,
    "image_path": image,
    "session_number": sessionNumber,
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

def getTimeStamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp