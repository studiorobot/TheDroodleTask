from conversationManagement.conversationTools.conversationTools import encodeMessageInternal

class featureExtractor:
    def __init__(self, vision_model: str, image_path: str, client):
        print(f"FeatureExtractor initialized with model: {vision_model} and image: {image_path}")
        """
        Initializes the FeatureExtractor with a vision model and an image path.
        """
        self.vision_model = vision_model
        self.image_path = image_path
        self.client = client # NOT SURE IF THIS IS NEEDED
        self.features = None

    def extract_features(self, client) -> str:
        """
        Uses OpenAI's vision capabilities to extract abstract features from the image.
        """
        # Define the vision prompt
        vision_prompt = (
            "Please analyze the image and identify abstract objects. Do NOT mention literal objects like cars, trees, or people. Instead, describe abstract elements such as lines, shapes, clusters and their relative positioning. The response should be 20 words or less, a few descriptions."
        )

        # Create the message dictionary
        vision_message = encodeMessageInternal(
            textMessage=vision_prompt,
            timestamp="",
            role="system",
            assistantType="LLM",
            image=self.image_path
        )

        # print("Extracted Features")

        try:
            # Send the request using the OpenAI client
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[vision_message]
            )
            # Extract the content from the response
            self.features = response.choices[0].message.content.strip()
            return self.features
        except Exception as e:
            print(f"An error occurred while extracting features: {e}")
            self.features = None
            raise

    def augment_user_message(self, user_message: str) -> str:
        """
        Appends the extracted features to the user's message.
        """
        if not self.features or self.features.strip() == "":
            raise ValueError("No valid features were extracted. Check the feature extraction process.")
        return f"{user_message}\n\nAbstract shapes: {self.features}"
    
    def augment_constant_prompt(self, constant_prompt: str) -> str:
        """
        Appends the extracted features to the constant prompt.
        """
        if not self.features or self.features.strip() == "":
            raise ValueError("No valid features were extracted. Check the feature extraction process.")
        return f"{constant_prompt}\n\nAbstract shapes: {self.features}"