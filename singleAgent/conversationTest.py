from standardConversation import standardConversation
from controlledConversation import controlledConversation

print("STANDRAD CONVERSATION TEST----------------------------------")
prompts = ["This is prompt 1", "This is prompt 2"]
conv = standardConversation("gpt-4o", prompts, "stdConvClassTest")
conv.contConversation("userMesage")
print(conv.makeRequest())
print(conv.getPrompts())
conv.insertMessage("new direction to take", "system")
conv.contConversation("woah noew human message")
conv.makeConversationSave()

print(conv.getConversation())

print("CONTROLLED CONVERSATION TEST--------------------------------")
controlPrompts = ["this is controll prompt 1", "this is controll prompt 2"]
controlConv = controlledConversation("gpt4o", "gpt4o", prompts, controlPrompts, "controlConvClassTest")

controlConv.contConversation("userMessage")
print(controlConv.getControlPrompts())
print(controlConv.makeJudegement())
print(controlConv.makeRequest())
controlConv.makeConversationSave()
