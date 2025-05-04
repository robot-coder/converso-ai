from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import httpx
import os
from starlette.middleware.cors import CORSMiddleware

# Assuming liteLLM is a placeholder for an actual LLM client library
import liteLLM

app = FastAPI(title="Web-based Chat Assistant")

# Allow CORS for frontend deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state to store conversations and models
conversations = {}
available_models = ["model-A", "model-B", "model-C"]
current_model = "model-A"

# Directory to store uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatMessage(BaseModel):
    user_id: str
    message: str
    model: Optional[str] = None  # Optional override for model selection

class ModelSelection(BaseModel):
    model_name: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """
    Serve the main HTML page.
    """
    with open("index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/set_model")
async def set_model(selection: ModelSelection):
    """
    Set the current model for conversations.
    """
    global current_model
    if selection.model_name not in available_models:
        raise HTTPException(status_code=400, detail="Model not available")
    current_model = selection.model_name
    return {"status": "success", "model": current_model}

@app.post("/upload_files")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload files to be used as context.
    """
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            saved_files.append(file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save {file.filename}: {str(e)}")
    return {"uploaded_files": saved_files}

@app.post("/chat")
async def chat_endpoint(chat: ChatMessage):
    """
    Handle user message, maintain conversation context, and return LLM response.
    """
    user_id = chat.user_id
    message = chat.message
    model_name = chat.model or current_model

    # Initialize conversation history if not exists
    if user_id not in conversations:
        conversations[user_id] = []

    # Append user message to history
    conversations[user_id].append({"role": "user", "content": message})

    # Prepare context from uploaded files
    context_texts = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            with open(file_path, "r") as f:
                context_texts.append(f.read())
        except Exception:
            continue
    context = "\n".join(context_texts)

    # Build prompt with context and conversation history
    prompt = ""
    if context:
        prompt += f"Context:\n{context}\n\n"
    for turn in conversations[user_id]:
        role = turn["role"]
        content = turn["content"]
        prompt += f"{role.capitalize()}: {content}\n"
    prompt += f"Assistant:"

    # Call the LLM API (liteLLM assumed to be a client library)
    try:
        response_text = await generate_response(prompt, model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    # Append assistant response to history
    conversations[user_id].append({"role": "assistant", "content": response_text})

    return {"response": response_text}

@app.post("/compare")
async def compare_models(chat: ChatMessage):
    """
    Generate responses from two models and return both for comparison.
    """
    user_id = chat.user_id
    message = chat.message

    # Initialize conversation history if not exists
    if user_id not in conversations:
        conversations[user_id] = []

    # Append user message
    conversations[user_id].append({"role": "user", "content": message})

    # Prepare context from uploaded files
    context_texts = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            with open(file_path, "r") as f:
                context_texts.append(f.read())
        except Exception:
            continue
    context = "\n".join(context_texts)

    # Build prompt
    prompt = ""
    if context:
        prompt += f"Context:\n{context}\n\n"
    for turn in conversations[user_id]:
        role = turn["role"]
        content = turn["content"]
        prompt += f"{role.capitalize()}: {content}\n"
    prompt += f"Assistant:"

    # Generate responses from two models
    try:
        response_model_a = await generate_response(prompt, "model-A")
        response_model_b = await generate_response(prompt, "model-B")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    # Append responses to history
    conversations[user_id].append({"role": "assistant", "content": response_model_a})
    conversations[user_id].append({"role": "assistant", "content": response_model_b})

    return {
        "model_a_response": response_model_a,
        "model_b_response": response_model_b
    }

async def generate_response(prompt: str, model_name: str) -> str:
    """
    Generate a response from the LLM given a prompt and model name.
    """
    # Placeholder implementation; replace with actual liteLLM API call
    # For example:
    # response = liteLLM.generate(prompt=prompt, model=model_name)
    # return response.text

    # Mock response for demonstration
    # In real implementation, replace with actual API call
    async with httpx.AsyncClient() as client:
        try:
            # Example API call to a hypothetical endpoint
            response = await client.post(
                "https://api.liteLLM.com/generate",
                json={"prompt": prompt, "model": model_name}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("text", "Sorry, I couldn't generate a response.")
        except Exception:
            # Fallback mock response
            return f"Mock response from {model_name} for prompt: {prompt[:50]}..."