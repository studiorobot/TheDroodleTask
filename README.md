# Single Agent Readme

### About

This repository contains code for the Droodles project's control scheme, operating as an added middle-man layer between the user and the LLM. Our hope is that it is useful as an example of how your team might manage the content of a conversation. Our implementation uses a hierarchical class structure for handling conversation content and prompting of the LLM. The `standardConversation` class implements core features, serving as a foundation for more complex content handling systems. At this moment, you can go read the classes that extend `standardConversation` but the speed at which those classes change has prevented us from writing documentation for them.

### The .env system

In order to make any request to the API, we need to be able to access some API endpoint using a given key. In this repository, keys are stored in a `.env`  file to ensure that they are not shared through Github. The file `EXAMPLE.env`  is provided as a template. Before doing anything, store any API keys you have in this file and rename it to `.env` .

### Message dictionary object system

The main functions of the classes in this repository take individual message dictionary objects as a parameter. The dictionary object should contain the following entries:

- `content`: the text of the message typed into the interface
- `timestamp`: the time recorded when the message was sent
- `role`: who sent the message, must follow a valid role (user, assistant, system)
- `image_path`: contains the path to an image to include in the message
- `session_number`: used to track which droodle is being discussed in experimental settings
- `assistant_type`: the kind of assistant is being used in the conversation
- `note`: for passing additional information to the system

Here’s an example of one of these dictionary objects:

```json
{
  "content": "hello",
  "timestamp": "2024-10-14 15:05:37",
  "role": "user",
  "image_path": "",
  "session_number": -1,
  "assistant_type": "LLM",
  "note": ""
}
```

It's recommended that these dictionary objects are used at all times when interacting with the standardConversation class.

### Conversation Tools Module

The conversation tools module contains functions that can be used in any script to easily create valid dictionary objects for interacting with the openAI API and other functions defined in the classes in this git repository. While this additional layer of abstraction is not strictly necessary, it simplifies the code and makes it easier to read.

Encode Message Internal: 

Creates a dictionary object following the structure described above. the input parameters follow the same rules described above with a few assumptions that can assigned alternate values at function call.

`encodeMessageInternal(textMessage: str, timestamp: str, role: str, assistantType: str, sessionNumber: int = -1, image: str = "", note: str = "") -> dict`

Encode Message:

Creates a dictionary object *according to the structure defined by openAI for sending to the OpenAI API*. Read the [openAI API documentation](https://platform.openai.com/docs/api-reference/chat/create) for more information on this. If given an image, the function also automatically decodes the image and adds this information into the message.

`encodeMessage(textMessage: str, role: str, imagePath: str = "") -> dict`

- textMessage: text content of the message
- role: which memeber of the conversation sent the message, must follow a message role (user, assistant, system).
- imagePath: path to the image to be included in the message.

Decode Image:

converts an image file into [the base64 format accepted by the openAI API](https://platform.openai.com/docs/guides/vision/uploading-base-64-encoded-images) for use with models that have vision (at the time of writing, this is only gpt-4o)

`decodeImage(imagePath: str) -> str`

### Standard Conversation Class

The standard conversation class is a middle-man system designed to simplify sending and receiving OpenAI API requests in addition to tracking and storing important information about the conversation taking place. The class abstracts the function of an LLM and The interface of the class is designed to reduce continued conversations to just a few simple functions.

Storage system:

One of the main functions of the standardConversation class is to automatically track an store conversation data. This is done through saving all the conversation dictionary objects in a JSON file in the conversationArchive folder in the repository. When a conversation takes place with an agent, these files keep track of all the messages that occurred in that conversation but do not automatically save until the `makeConversationSave` function is called.

Constructor:

`__init__(self, model: str, prompts: list[str], conversationName: str, savePath: str = 'conversationArchive')`

- Model: the name of the model being used using [openAI naming system](https://platform.openai.com/docs/models) (ex: "gpt-4o”, “gpt-3.5”, etc.)
- Prompts: a list of strings containing the prompts used at the beginning of every conversation
- conversationName: used in file naming to keep track of the kind of LLM prompting clear in data analysis. When a permanent file save is created, the conversationName is used at the beginning of the json file name.
- savePath: the root path in which all conversations are stored. Defaults to a folder called “conversationArchive”. The folder set here must be created *before* the constructor is called or an error will be thrown.

Functions:

- **Continue conversation with Dictionary**: takes a new message, makes a request for reply to LLM, stores new message and reply into conversation save, returns reply message dictionary object. If the new message contains an image path, the image automatically added into the message.
    
    `contConversationDict(self, newMessage: dict) -> dict`
    

- **Continue conversation with string**: takes new string message and possible string image path, makes request for reply to LLM, stores new message and reply into conversation save, returns reply message string. Assumes the following: time stamp is recorded when function is run, the new message is a user message, the session number is -1, the assistant type is LLM
    
    `contConversation(self, newMessage: str, imagePath: str = "") -> str`
    
    THIS FUNCTION IS CONSIDERED LEGACY AND SHOULD BE USED ONLY IF NECCESSARY
    

- **Insert message Dictionary**: takes a message Dictionary object and inserts it into the conversation without making a request to the LLM, stores new message into conversation save
    
    `insertMessageDict(self, newMessage: dict)`
    

- **Insert message String**: takes message string, role string, and potentially image path and note. Inserts new message into conversation, stores new message into conversation save. Assumes the following: time stamp is recorded when function is run, the session number is -1, the assistant type is LLM
    
    `insertMessage(self, newMessage: str, role: str, imagePath: str = "", note: str = "")`
    
    THIS FUNCTION IS CONSIDERED LEGACY AND SHOULD BE USED ONLY IF NECCESSARY
    

- **Turnover conversation dictionary**: Without adding a new user message, a request is made to the LLM and the reply is added to the conversation save.
    
    `turnoverConversationDict(self)`
    

- **Make conversation Save**: makes a permanent save file for the conversation. File is named using the conversationName defined at initialization and an 8 digit number based on the date at which the save was created.
    
    `makeConversationSave(self)`


- **Get Conversation**: Returns a list of message dictionary objects that represents the entire conversation thus far. Class member variables not modified.
    
    `getConversation(self) -> list[dict]`
    

- **Get Conversation String**: Returns a single string version of the conversation that has so far taken place. Class member variables not modified.
    
    `getConversationStr(self) -> str`
    

- **Get Prompts**: Returns a list of strings containing the prompts being used to make requests to the LLM. Class member variables not modified.
    
    `getPrompts(self) -> list[str]`