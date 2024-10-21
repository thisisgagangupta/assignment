import base64
import os
from art import text2art
from medmitra.models import responseDocument


def encode_images(images, inputDocument: responseDocument):
    for i, (filename, image) in enumerate(images.items()):
        image.save(filename, "PNG")
        # Read the saved image file as bytes
        with open(filename, "rb") as f:
            image_bytes = f.read()
        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        inputDocument.add_image(image_name=filename, image_data=image_base64)

        # Remove the temporary image file
        os.remove(filename)
