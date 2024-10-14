import base64 #used to turn image files into useable data for the api

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
