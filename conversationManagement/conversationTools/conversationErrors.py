#Catch all error for when something goes wrong that we don't have a specific error for
class conversationError(Exception):
    def __init__(self, message):
        self.message = message

#Error for when the decision LLM gives an unexpected response
class moduleExtractError(conversationError):
    def __init__(self, message):
        self.message = message