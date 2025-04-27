import os
import shutil
import fnmatch
import json

def clean_files(dataset_dir):
    """
    Deletes all Zone.Identifier files in the specified dataset directory.

    Args:
        dataset_dir (str): The path to the dataset directory.
    """
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            if file[-16:] == ":Zone.Identifier":
                print(f"Deleting file: {file}")
                file_path = os.path.join(root, file)
                os.remove(file_path)
            elif not (fnmatch.fnmatch(file, "droodleExample?.jpg????-????.json") or fnmatch.fnmatch(file, "droodleExample?.jpg.json")):
                print(f"Deleting file: {file}")
                file_path = os.path.join(root, file)
                os.remove(file_path)

def extract_captions(dataset_dir):
    """
    Extracts captions from the specified dataset directory.

    Args:
        dataset_dir (str): The path to the dataset directory.
    """

    captions = []
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            if file.endswith(".json") and file != "captions.json":
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                parent_dir = os.path.dirname(file_path)
                folder_name = os.path.basename(parent_dir)
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                    for message in conversation:
                        text = message.get("message", None)
                        if text is None:
                            text = message.get("content", None)
                        if text and (text.startswith("SUBMITTED CAPTION:") or text.startswith("User submitted caption:")):
                            if text.startswith("SUBMITTED CAPTION:"):
                                caption = text[19:]
                            else:
                                caption = text[24:]
                            captionData = {
                            "number": folder_name[:3],
                            "condition": folder_name[3:],
                            "caption": caption,
                            "droodle": ''.join(filter(str.isdigit, file_name.split('.')[0])),
                            "score": None
                            }
                            captions.append(captionData)
                            print(f"Caption extracted: {captionData}\n")

                    # Process the JSON data as needed
                    # For example, extract captions or other relevant information
    with open(os.path.join(dataset_dir, 'captions.json'), 'w') as f:
        json.dump(captions, f, indent=4)

#MAIN SCRIPT
dataset_directory = "../User Study Archive - Limited Dataset/"  # Adjust the path as needed
# clean_files(dataset_directory)
extract_captions(dataset_directory)

