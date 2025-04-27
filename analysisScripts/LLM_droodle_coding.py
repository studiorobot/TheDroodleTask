import sys
import os
from rich import print #Used to print colored text in the terminal

sys.path.append(os.path.abspath('..'))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Set the working directory to the parent directory

from conversationManagement.standardConversation.standardConversation import standardConversation
import json

def grade_caption(caption, agent):
    """
    Pass the caption to the LLM and ask for a score
    """
    caption_text = caption.get("caption")
    score = agent.makeTempMessage(caption_text, "droodleExamples/droodleExample1.jpg")
    caption["LLM_score"] = score
    return score

data = []

#Set the propmts and start up the agent
prompts = []
with open("analysisScripts/coding_prompt.txt", "r") as f:
    prompts.append(f.read())
agent = standardConversation("gpt-4o", prompts, "coding")

#get all the prototypic droodles and add them into the conversation
with open("analysisScripts/trey_prototypic_droodles.json", "r") as f:
    prototypic_droodles = json.load(f)
for droodle in prototypic_droodles:
    prototypic_caption = droodle.get("caption")
    prototypic_reasoning = droodle.get("reasoning")
    prototypic_score = droodle.get("score")
    agent.insertMessage(prototypic_caption, "user")
    agent.insertMessage(f"{prototypic_score} - {prototypic_reasoning}", "assistant")

#Load the caption data
with open("User Study Archive - Limited Dataset/captions.json", "r") as f:
    data = json.load(f)

droodle_number = 1
print(f"[blue]Grading all captions for droodle {droodle_number}[/blue]\n")
for caption in data:
    if caption.get("LLM_score") is None and caption.get("droodle") == str(droodle_number):
        print(f"Caption: {caption.get('caption')}\n")
        ai_score = grade_caption(caption, agent)
        human_score = caption.get("score")
        print(f"Human Score: {human_score}, AI Score: {ai_score}\n")