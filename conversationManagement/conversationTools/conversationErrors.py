import logging

# Base Error Class--------------------------------------------------------

#Catch all error for when something goes wrong that we don't have a specific error for
class ConversationError(Exception):
    def __init__(self, message: str):
        self.message = message
        logging.error("Conversation Error: "+message)

class InvalidInitVariableError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Invalid Init Variable Error: "+message)

# Standard Conversation Errors--------------------------------------------

# Raised when the storage folder is not found or cannot be accessed
class StorageFolderNotFoundError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Storage Folder Not Found Error: " + message)

# Raised when a message struct is missing key components or has improper values
class ImproperMessageStructError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Improper Message Data Struct Error: " + message)

# Raised when the .env file is improperly defined or missing key components
class InvalidEnvError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Invalid Env Error: " + message)

# Raised when a prompt array is formatted poorly
class ImproperPromptFormatError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Improper Prompt Format Error: " + message)

# Modular Conversation Errors--------------------------------------------

# Raised when a decision is out of the bounds of valid decisions
class SwitchOutOfBoundsError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Switch Out Of Bounds Error: " + message)

#Error for when the decision LLM gives an unexpected response
class moduleExtractError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Module Extract Error: "+message)

# Conversation Tools Errors--------------------------------------------

# Raised when an image file is not found at the specified location
class ImageFileNotFoundError(ConversationError):
    def __init__(self, message: str):
        self.message = message
        logging.error("Image File Not Found Error: " + message)

