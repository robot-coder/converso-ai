# README.md

# Web-based Chat Assistant

This project is a web-based Chat Assistant that allows users to have continuous conversations with a Large Language Model (LLM). Users can select different models, upload files for context, and optionally compare responses from two models. The application is designed to be deployed on Render.com for easy access and scalability.

## Features

- Interactive chat interface with persistent conversation context
- Model selection from available LLMs
- Upload files to provide additional context to the models
- Optional comparison of responses from two different models
- Deployed on Render.com for cloud hosting

## Technologies Used

- FastAPI for the backend API
- Uvicorn as the ASGI server
- liteLLM for lightweight LLM interactions
- httpx for HTTP requests
- starlette for web server utilities
- pydantic for data validation

## Files

- `index.html`: Front-end UI for user interaction
- `app.py`: Backend API implementation
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Access to Render.com for deployment

### Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running Locally

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

Open your browser and navigate to `http://127.0.0.1:8000` to access the chat interface.

### Deployment

Configure your deployment on Render.com by setting the start command to:

```bash
uvicorn app:app --host 0.0.0.0 --port 10000
```

and ensure all dependencies are included in `requirements.txt`.

## Usage

- Enter your message in the chat input box.
- Select the desired model from the dropdown.
- Upload files to provide additional context.
- Use the compare feature to see responses from two models side-by-side.

## License

This project is licensed under the MIT License.

---

# index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Chat Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #chat { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
        .message { margin: 5px 0; }
        .user { font-weight: bold; }
        .bot { color: blue; }
        #modelSelect, #compareCheckbox { margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Web-based Chat Assistant</h1>
    <div id="chat"></div>
    <form id="chatForm">
        <input type="text" id="messageInput" placeholder="Type your message" required />
        <button type="submit">Send</button>
    </form>
    <div id="modelSelect">
        <label for="model">Select Model:</label>
        <select id="model">
            <option value="model1">Model 1</option>
            <option value="model2">Model 2</option>
        </select>
    </div>
    <div>
        <label><input type="checkbox" id="compareCheckbox" /> Compare responses from two models</label>
    </div>
    <div>
        <input type="file" id="fileUpload" multiple />
        <button id="uploadBtn">Upload Files</button>
    </div>
    <script>
        const chatDiv = document.getElementById('chat');
        const form = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const modelSelect = document.getElementById('model');
        const compareCheckbox = document.getElementById('compareCheckbox');
        const fileInput = document.getElementById('fileUpload');
        const uploadBtn = document.getElementById('uploadBtn');

        let conversationHistory = [];
        let uploadedFiles = [];

        function appendMessage(sender, message) {
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message ' + sender;
            msgDiv.innerText = sender.toUpperCase() + ': ' + message;
            chatDiv.appendChild(msgDiv);
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }

        uploadBtn.onclick = () => {
            uploadedFiles = Array.from(fileInput.files);
            alert(`${uploadedFiles.length} files uploaded.`);
        };

        form.onsubmit = async (e) => {
            e.preventDefault();
            const message = messageInput.value;
            appendMessage('user', message);
            conversationHistory.push({ role: 'user', content: message });
            messageInput.value = '';

            const data = {
                message: message,
                model: modelSelect.value,
                history: conversationHistory,
                files: uploadedFiles.map(file => ({ name: file.name, content: null })), // Files can be processed as needed
                compare: compareCheckbox.checked
            };

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();

                if (result.responses) {
                    // Multiple responses for comparison
                    result.responses.forEach((resp, index) => {
                        appendMessage(`model${index + 1}`, resp);
                        conversationHistory.push({ role: 'assistant', content: resp });
                    });
                } else {
                    appendMessage('bot', result.response);
                    conversationHistory.push({ role: 'assistant', content: result.response });
                }
            } catch (error) {
                appendMessage('bot', 'Error: ' + error.message);
            }
        };
    </script>
</body>
</html>
```

# app.py

```python
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import tempfile
import traceback

# Placeholder for liteLLM import
# from liteLLM import load_model, generate_response

app = FastAPI()

# Load available models (placeholder)
AVAILABLE_MODELS = ['model1', 'model2', 'model3']

class ChatRequest(BaseModel):
    message: str
    model: str
    history: List[Dict[str, str]] = []
    files: Optional[List[Dict[str, Any]]] = None
    compare: bool = False

class ChatResponse(BaseModel):
    response: str
    responses: Optional[List[str]] = None

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        model_name = data.get("model")
        history = data.get("history", [])
        files = data.get("files", [])
        compare = data.get("compare", False)

        # Validate model
        if model_name not in AVAILABLE_MODELS:
            return JSONResponse(status_code=400, content={"error": "Selected model is not available."})

        # Process uploaded files if any
        # For simplicity, assume files are not processed in this placeholder
        # In production, read file contents and include as context

        # Generate response from the selected model
        response1 = generate_llm_response(message, model_name, history, files)

        responses = [response1]

        if compare:
            # Generate response from a second model (for comparison)
            other_model = AVAILABLE_MODELS[0] if model_name != AVAILABLE_MODELS[0] else AVAILABLE_MODELS[1]
            response2 = generate_llm_response(message, other_model, history, files)
            responses.append(response2)

        if compare:
            return ChatResponse(response="", responses=responses)
        else:
            return ChatResponse(response=response1)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

def generate_llm_response(message: str, model_name: str, history: List[Dict[str, str]], files: List[Dict[str, Any]]) -> str:
    """
    Generate a response from the LLM based on the message, model, history, and uploaded files.
    This is a placeholder implementation.
    """
    # In a real implementation, load the model and generate a response
    # For example:
    # model = load_model(model_name)
    # context = build_context(history, files)
    # response = model.generate(message, context)
    # return response

    # Placeholder response
    return f"[{model_name}] Echo: {message}"

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
```

# requirements.txt

```
fastapi
uvicorn
liteLLM
httpx
starlette
pydantic
```