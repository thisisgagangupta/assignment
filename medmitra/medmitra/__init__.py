from typing import Any
import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from marker.models import load_all_models
from pydantic import BaseModel


class SharedState(BaseModel):
    model_list: Any = None
    vision_model: Any = None
    vision_processor: Any = None
    crawler: Any = None


shared_state = SharedState()


def load_model(load_documents: bool):
    global shared_state
    
    # Force CPU usage
    device = "cpu"  
    if load_documents:
        print("[LOG] ✅ Loading OCR Model")
        shared_state.model_list = load_all_models()
        
        print("[LOG] ✅ Loading Vision Model")
        try:
            # Load the vision model and processor, explicitly setting device to CPU
            shared_state.vision_model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Florence-2-base", trust_remote_code=True
            ).to(device)  # Use "cpu" here
            shared_state.vision_processor = AutoProcessor.from_pretrained(
                "microsoft/Florence-2-base", trust_remote_code=True
            ) 
            # getting error and image functionality processing not working properly due to flash attention (flash_attn) not working on cpu
        except ImportError as e:
            print(f"Skipping flash_attn-related model components. Error: {str(e)}")


def get_shared_state():
    return shared_state


def get_active_models():
    print(shared_state)
    return shared_state