import warnings
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from medmitra import load_model #changed
from medmitra.documents.router import document_router
from medmitra.image.router import image_router
from medmitra.demo import demo_ui

# logging.basicConfig(level=logging.DEBUG)
import gradio as gr

warnings.filterwarnings(
    "ignore", category=UserWarning
)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(document_router, prefix="/parse_document", tags=["Documents"])
app.include_router(image_router, prefix="/parse_image", tags=["Images"])
app = gr.mount_gradio_app(app, demo_ui, path="")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the server.")
    parser.add_argument("--host", default="0.0.0.0", help="Host IP address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--documents", action="store_true", help="Load document models")
    parser.add_argument("--reload", action="store_true", help="Reload Server")
    args = parser.parse_args()

    # Set global variables based on parsed arguments
    load_model(args.documents)

    # Conditionally include routers based on arguments
    app.include_router(
        document_router,
        prefix="/parse_document",
        tags=["Documents"],
        include_in_schema=args.documents,
    )
    app.include_router(
        image_router,
        prefix="/parse_image",
        tags=["Images"],
        include_in_schema=args.documents,
    )

    # Start the server
    import uvicorn

    uvicorn.run("server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()