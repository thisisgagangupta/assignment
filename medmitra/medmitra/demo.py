import os
import base64
import mimetypes
import requests
from PIL import Image
from io import BytesIO
import gradio as gr

single_task_list = [
    "Caption",
    "Detailed Caption",
    "More Detailed Caption",
    "OCR",
    "OCR with Region",
]

header_markdown = """

#

## MedMitra

"""


def decode_base64_to_pil(base64_str):
    return Image.open(BytesIO(base64.b64decode(base64_str)))


def parse_document(input_file_path, parameters, request: gr.Request):
    # Validate file extension
    allowed_extensions = [".pdf", ".doc"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")
    try:
        host_url = request.headers.get("host")

        post_url = f"http://{host_url}/parse_document"
        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found

        with open(input_file_path, "rb") as f:
            files = {"file": (input_file_path, f, mime_type)}
            response = requests.post(
                post_url, files=files, headers={"accept": "application/json"}
            )

        document_response = response.json()

        images = document_response.get("images", [])

        # Decode each base64-encoded image to a PIL image
        pil_images = [
            decode_base64_to_pil(image_dict["image"]) for image_dict in images
        ]

        return (
            str(document_response["text"]),
            gr.Gallery(value=pil_images, visible=True),
            str(document_response["text"]),
            gr.JSON(value=document_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


def process_image(input_file_path, parameters, request: gr.Request):
    print(parameters)
    # Validate file extension
    allowed_image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_image_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")

    try:
        host_url = request.headers.get("host")

        # URL for image parsing
        post_url = f"http://{host_url}/parse_image/process_image"

        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found
        with open(input_file_path, "rb") as f:
            # Prepare the files payload
            files = {
                "image": (input_file_path, f, mime_type),
            }

            # Prepare the data payload
            data = {"task": parameters}

            # Send the POST request
            response = requests.post(
                post_url, files=files, data=data, headers={"accept": "application/json"}
            )

        image_process_response = response.json()

        images = image_process_response.get("images", [])
        # Decode each base64-encoded image to a PIL image
        pil_images = [
            decode_base64_to_pil(image_dict["image"]) for image_dict in images
        ]

        # Decode the image if present in the response
        # images = document_response.get('image', {})
        # pil_images = [decode_base64_to_pil(base64_str) for base64_str in images.values()]

        return (
            gr.update(value=image_process_response["text"]),
            gr.Gallery(value=pil_images, visible=(len(images) != 0)),
            gr.JSON(value=image_process_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


def parse_image(input_file_path, parameters, request: gr.Request):
    # Validate file extension
    allowed_image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_image_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")

    try:
        host_url = request.headers.get("host")

        # URL for image parsing
        post_url = f"http://{host_url}/parse_image/image"

        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found

        with open(input_file_path, "rb") as f:
            files = {"file": (input_file_path, f, mime_type)}
            response = requests.post(
                post_url, files=files, headers={"accept": "application/json"}
            )

        document_response = response.json()

        # Decode the image if present in the response
        images = document_response.get("images", [])

        # Decode each base64-encoded image to a PIL image
        pil_images = [
            decode_base64_to_pil(image_dict["image"]) for image_dict in images
        ]

        return (
            gr.update(value=document_response["text"]),
            gr.Gallery(value=pil_images, visible=True),
            gr.update(value=document_response["text"]),
            gr.update(value=document_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")



# ui

demo_ui = gr.Blocks(theme=gr.themes.Monochrome(radius_size=gr.themes.sizes.radius_none))

with demo_ui:
    with gr.Tabs():
        with gr.TabItem("Documents"):
            with gr.Row():
                with gr.Column(scale=80):
                    document_file = gr.File(
                        label="Upload Document",
                        type="filepath",
                        file_count="single",
                        interactive=True,
                        file_types=[".pdf", ".ppt", ".doc", ".pptx", ".docx"],
                    )
                    with gr.Accordion("Parameters", visible=True):
                        document_parameter = gr.Dropdown(
                            [
                                "Fixed Size Chunking",
                                "Regex Chunking",
                                "Semantic Chunking",
                            ],
                            label="Chunking Strategy",
                        )
                        if document_parameter == "Fixed Size Chunking":
                            document_chunk_size = gr.Number(
                                minimum=250, maximum=10000, step=100, show_label=False
                            )
                            document_overlap_size = gr.Number(
                                minimum=250, maximum=1000, step=100, show_label=False
                            )
                    document_button = gr.Button("Parse Document")
                with gr.Column(scale=200):
                    with gr.Accordion("Markdown"):
                        document_markdown = gr.Markdown()
                    with gr.Accordion("Extracted Images"):
                        document_images = gr.Gallery(visible=False)
                    with gr.Accordion("Chunks", visible=False):
                        document_chunks = gr.Markdown()
            with gr.Accordion("JSON Output"):
                document_json = gr.JSON(label="Output JSON", visible=False)

        with gr.TabItem("Images"):
            with gr.Tabs():
                with gr.TabItem("Process"):
                    with gr.Row():
                        with gr.Column(scale=80):
                            image_process_file = gr.File(
                                label="Upload Image",
                                type="filepath",
                                file_count="single",
                                interactive=True,
                                file_types=[".jpg", ".jpeg", ".png"],
                            )
                            image_process_parameter = gr.Dropdown(
                                choices=single_task_list,
                                label="Task Prompt",
                                value="Caption",
                                interactive=True,
                            )
                            image_process_button = gr.Button("Process Image")
                        with gr.Column(scale=200):
                            image_process_output_text = gr.Textbox(label="Output Text")
                            image_process_output_image = gr.Gallery(
                                label="Output Image ⌛", interactive=False
                            )
                    with gr.Accordion("JSON Output"):
                        image_process_json = gr.JSON(label="Output JSON", visible=False)
                    
                with gr.TabItem("Parse"):
                    with gr.Row():
                        with gr.Column(scale=80):
                            image_parse_file = gr.File(
                                label="Upload Image",
                                type="filepath",
                                file_count="single",
                                interactive=True,
                            )
                            with gr.Accordion("Parameters", visible=False):
                                image_parse_parameter = gr.CheckboxGroup(
                                    ["chunk document"], show_label=False
                                )
                            image_parse_button = gr.Button("Parse Image")
                        with gr.Column(scale=200):
                            with gr.Accordion("Markdown"):
                                image_parse_markdown = gr.Markdown()
                            with gr.Accordion("Extracted Images"):
                                image_parse_images = gr.Gallery(visible=False)
                            with gr.Accordion("Chunks", visible=False):
                                image_parse_chunks = gr.Markdown()
                    with gr.Accordion("JSON Output"):
                        image_parse_json = gr.JSON(label="Output JSON", visible=False)
                        

    document_button.click(
        fn=parse_document,
        inputs=[document_file, document_parameter],
        outputs=[document_markdown, document_images, document_chunks, document_json],
    )
    image_parse_button.click(
        fn=parse_image,
        inputs=[image_parse_file, image_parse_parameter],
        outputs=[
            image_parse_markdown,
            image_parse_images,
            image_parse_chunks,
            image_parse_json,
        ],
    )
    image_process_button.click(
        fn=process_image,
        inputs=[image_process_file, image_process_parameter],
        outputs=[
            image_process_output_text,
            image_process_output_image,
            image_process_json,
        ],
    )
