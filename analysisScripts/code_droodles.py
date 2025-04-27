import json
import os
from rich import print


def grade_caption(caption):
    """
    Pass the caption to the user through the terminal and ask for a score
    """
    caption_text = caption.get("caption")
    droodle_number = caption.get("droodle")
    score = caption.get("score")
    reasoning = caption.get("reasoning")
    print(f"[red] Droodle {droodle_number}:[/red] {caption_text}")
    print(f"[blue] Current Score:[/blue] {score}")
    print(f"[blue] Current Reasoning:[/blue] {reasoning}\n")
    score = input("Enter a score (1-4) or press *enter* to keep current score: \n")
    while score not in ["1", "2", "3", "4", ""]:
        print("Invalid score. Please enter a number between 1 and 4.\n")
        score = input("Enter a score (1-4): ")
    if score != "":
        caption["score"] = int(score)
    reasoning = input("Enter a reasoning for the score or press *enter* to keep current reasoning: \n")
    if reasoning != "":
        caption["reasoning"] = reasoning

    

data = []

with open("../User Study Archive - Limited Dataset/captions.json", "r") as f:
    data = json.load(f)

i = 0
droodle_number = 0
for droodle_number in range(1, 5):
    print(f"[blue]Grading all captions for droodle {droodle_number}[/blue]\n")
    for item in data:
        if item.get("droodle") == str(droodle_number):
            grade_caption(item)
            i += 1
        if i >= 4:
            with open ("../User Study Archive - Limited Dataset/captions.json", "w") as f:
                json.dump(data, f, indent=4)
            print("[blue]Saving...[/blue]\n")
            i = 0

print("[green]All captions graded![/green]\n")

print("[blue]Removing Duplicate Captions...[/blue]\n")
# Remove duplicates from the list
for item in data:
    test_number = item.get("number")
    droodle_number = item.get("droodle")
    score = item.get("score")
    while True:
        for other_item in data:
            if other_item.get("number") == test_number and other_item.get("droodle") == droodle_number and item != other_item and score <= other_item.get("score"):
                data.remove(other_item)
                continue
        break

unique_data = []
for item in data:
    if item not in unique_data:
        unique_data.append(item)

data = unique_data

with open ("../User Study Archive - Limited Dataset/captions.json", "w") as f:
    json.dump(data, f, indent=4)

print("[blue]Saving...[/blue]\n")