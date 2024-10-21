import os
import tempfile
import subprocess

from marker.convert import convert_single_pdf
from medmitra.utils import encode_images
from medmitra.models import responseDocument


# Function to handle PDF parsing
def parse_pdf(input_data, model_state) -> responseDocument:
    try:
        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            ) as temp_pdf_file:
                temp_pdf_file.write(input_data)
                temp_pdf_path = temp_pdf_file.name

            input_path = temp_pdf_path
            cleanup_tempfile = True

        elif isinstance(input_data, str) and input_data.endswith(".pdf"):
            input_path = input_data
            cleanup_tempfile = False

        else:
            raise ValueError(
                "Invalid input data format. Expected bytes or PDF file path."
            )

        full_text, images, out_meta = convert_single_pdf(
            input_path, model_state.model_list
        )

        parse_pdf_result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, parse_pdf_result)

        if cleanup_tempfile:
            os.remove(input_path)

        return parse_pdf_result

    except Exception as e:
        raise RuntimeError(f"Error parsing PPT: {str(e)}")


# Function to handle PPT and DOC parsing
def parse_ppt(input_data, model_state) -> responseDocument:
    try:
        if isinstance(input_data, bytes):
            print("Recieved ppt file")
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(input_data)
                tmp_file.flush()
                input_path = tmp_file.name

        elif isinstance(input_data, str) and (
            input_data.endswith(".ppt")
            or input_data.endswith(".pptx")
            or input_data.endswith(".doc")
            or input_data.endswith(".docx")
        ):
            input_path = input_data

        else:
            raise ValueError(
                "Invalid input data format. Expected bytes or PPT/DOC file path."
            )

        if input_path.endswith((".ppt", ".pptx", ".doc", ".docx")):
            output_dir = tempfile.mkdtemp()
            command = [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                input_path,
            ]
            subprocess.run(command, check=True)
            output_pdf_path = os.path.join(
                output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            input_path = output_pdf_path

        full_text, images, out_meta = convert_single_pdf(
            input_path, model_state.model_list
        )
        images = encode_images(images)

        parse_ppt_result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, parse_ppt_result)

        if input_data != input_path:
            os.remove(input_path)

        return parse_ppt_result

    except Exception as e:
        raise RuntimeError(f"Error parsing PPT: {str(e)}")


def parse_doc(input_data, model_state) -> responseDocument:
    try:
        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(input_data)
                tmp_file.flush()
                input_path = tmp_file.name

        elif isinstance(input_data, str) and (
            input_data.endswith(".ppt")
            or input_data.endswith(".pptx")
            or input_data.endswith(".doc")
            or input_data.endswith(".docx")
        ):
            input_path = input_data

        else:
            raise ValueError(
                "Invalid input data format. Expected bytes or PPT/DOC file path."
            )

        if input_path.endswith((".ppt", ".pptx", ".doc", ".docx")):
            output_dir = tempfile.mkdtemp()
            command = [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                input_path,
            ]
            subprocess.run(command, check=True)
            output_pdf_path = os.path.join(
                output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            input_path = output_pdf_path

        full_text, images, out_meta = convert_single_pdf(
            input_path, model_state.model_list
        )
        images = encode_images(images)

        parse_doc_result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, parse_doc_result)

        if input_data != input_path:
            os.remove(input_path)

        return parse_doc_result

    except Exception as e:
        raise RuntimeError(f"Error parsing PPT: {str(e)}")