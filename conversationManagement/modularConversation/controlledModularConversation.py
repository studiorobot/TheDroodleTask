from ..modularConversation.modularConversation import modularConversation, module #parent 
from ..standardConversation.standardConversation import standardConversation #controller 
from ..conversationTools import encodeMessage, encodeMessageInternal #message encoder
import re #used to do a better extraction from controller responses
from datetime import datetime #used to retrieve date and time for file name

class controlledModularConversation(modularConversation):
    def __init__(self, model: str, constantPrompt: list[str], modulePrompts: list[str], controlPrompts: list[str], conversationName: str, savePath: str = 'conversationArchive', imageFeatures=None):
        super().__init__(model, constantPrompt, modulePrompts, conversationName, savePath)
        self._controller = standardConversation(model, [controlPrompts[0]], conversationName + " - Controller", savePath)
        self.image_features = imageFeatures  # Pre-processed image features, if provided
        self._argument_agents = []  # List of agents used to make arguments for their respective modules
        
        # Create agents for each module
        for indevModule in self.allModules():
            agent_name = conversationName + " - " + indevModule.name
            agent_prompt = [controlPrompts[1], modulePrompts[indevModule.value]]
            agent = standardConversation(model, agent_prompt, agent_name, savePath)
            self._argument_agents.append(agent)

    def set_image_features(self, image_features):
        self.image_features = image_features  # Update features as needed

    def set_current_image(self, image_path):
        self.current_image = image_path

    # Retrive the controller given by the index and get their decision
    def decideSwitch(self) -> module:
        #Get the chat history
        message = self.getConversationStr()

        #make and append the extrapolations
        #Add marker
        message = message + "Examples:\n"

        #get extrapolations
        possibleModules = self.allModules()
        extrapolations = self.get_module_arguments(possibleModules)
        

        #put all the extrapolations in one string
        extrapolationsStr = ""
        for i in range(len(possibleModules)):
            possibleMessage = extrapolations[i]
            indevModule = possibleModules[i]
            extrapolationsStr = extrapolationsStr + "Assistant - " + indevModule.name + "(" + str(indevModule.value) + ")> "+possibleMessage.get("content")+"\n"

        #append extrapolations
        message = message + "\n\n" + extrapolationsStr
        
        #Package the new message
        messageDict = encodeMessageInternal(message, "", "user", "Controller")
        
        #make the request
        reply = self._controller.contConversationDict(messageDict).get("content")

        return module(int(re.search(r'\d+', reply).group()))
    
    def get_module_arguments(self, modules: list[module]) -> list[dict]:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #get timestamp

        #make a message containing the last two messages from the conversation
        formattedMessage = encodeMessageInternal(self._getLastTwoMessages(), timestamp, "user", "LLM")
        outputMessages = []

        #Call each agent to get their argument
        for agent in self._argument_agents:
            message = agent.contConversationDict(formattedMessage)
            outputMessages.append(message)
        return outputMessages
    
    #Main function for continuing the conversation using a message dict object
    def contConversationDict(self, newMessage: dict) -> dict:
        self.insertMessageDict(newMessage) #Add new message
        self.switchStateUnbounded(self.decideSwitch()) #Switch the state
        outMessage = self.turnoverConversationDict()
        return outMessage
    
    def _getLastTwoMessages(self) -> str:
        #get the last two messages (or one if there is only one)
        if len(self._conversationInternal) >= 2:
            lastMessages = self._conversationInternal[-2:] #get the last two messages
        else:
            lastMessages = self._conversationInternal[-1:] #get the last message
        
        #Format the output
        output = ""
        for message in lastMessages:
            output = output + message.get("role")
            output = output + "> "
            output = output + message.get("content") + "\n"
        return output