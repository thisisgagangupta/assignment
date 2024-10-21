import os
import tempfile
import subprocess

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from medmitra import get_shared_state

from marker.convert import convert_single_pdf
from medmitra.utils import encode_images
from medmitra.models import responseDocument

document_router = APIRouter()
model_state = get_shared_state()


# Document parsing endpoints
@document_router.post("/pdf")
async def parse_pdf_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        full_text, images, out_meta = convert_single_pdf(
            file_bytes, model_state.model_list
        )

        result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, result)
        # result : responseDocument = convert_single_pdf(file_bytes , model_state.model_list)

        return JSONResponse(content=result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Document parsing endpoints
@document_router.post("/ppt")
async def parse_ppt_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ppt") as tmp_ppt:
        tmp_ppt.write(await file.read())
        tmp_ppt.flush()
        input_path = tmp_ppt.name

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

    with open(output_pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    full_text, images, out_meta = convert_single_pdf(pdf_bytes, model_state.model_list)

    os.remove(input_path)
    os.remove(output_pdf_path)
    os.rmdir(output_dir)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(images, result)

    return JSONResponse(content=result.model_dump())


@document_router.post("/docs")
async def parse_doc_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ppt") as tmp_ppt:
        tmp_ppt.write(await file.read())
        tmp_ppt.flush()
        input_path = tmp_ppt.name

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

    with open(output_pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    full_text, images, out_meta = convert_single_pdf(pdf_bytes, model_state.model_list)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(images, result)

    return JSONResponse(content=result.model_dump())


@document_router.post("")
async def parse_any_endpoint(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".ppt", ".pptx", ".doc", ".docx"}
    file_ext = os.path.splitext(file.filename)[1]

    if file_ext.lower() not in allowed_extensions:
        return JSONResponse(
            content={
                "message": "Unsupported file type. Only PDF, PPT, and DOCX are allowed."
            },
            status_code=400,
        )

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(await file.read())
        tmp_file.flush()
        input_path = tmp_file.name

    if file_ext.lower() in {".ppt", ".pptx", ".doc", ".docx"}:
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

    # Common parsing logic
    full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)

    os.remove(input_path)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(images, result)

    return JSONResponse(content=result.model_dump())