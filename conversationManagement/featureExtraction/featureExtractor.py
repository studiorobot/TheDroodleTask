from conversationManagement.conversationTools.conversationTools import encodeMessageInternal

class FeatureExtractor:
    def __init__(self, vision_model: str, image_path: str):
        """
        Initializes the FeatureExtractor with a vision model and an image path.
        """
        self.vision_model = vision_model
        self.image_path = image_path
        self.features = None

    def extract_features(self, client) -> str:
        """
        Uses OpenAI's vision capabilities to extract abstract features from the image.
        """
        # Define the vision prompt
        vision_prompt = (
            "Please analyze the image and identify abstract objects. "
            "Do NOT mention literal objects like cars, trees, or people. "
            "Instead, describe abstract elements such as lines, shapes, clusters and how they are positioned with respect to each other etc."
        )

        # Create the message dictionary
        vision_message = encodeMessageInternal(
            textMessage=vision_prompt,
            timestamp="",
            role="system",
            assistantType="LLM",
            image=self.image_path
        )

        # Send the request using the OpenAI client
        response = client.chat.completions.create(
            model=self.vision_model,
            messages=[vision_message]
        )

        # Extract the content from the response
        self.features = response.choices[0].message.content.strip()
        return self.features

    def augment_user_message(self, user_message: str) -> str:
        """
        Appends the extracted features to the user's message.
        """
        if not self.features:
            raise ValueError("Features have not been extracted. Call extract_features first.")
        return f"{user_message}\n\nAbstract shapes: {self.features}"