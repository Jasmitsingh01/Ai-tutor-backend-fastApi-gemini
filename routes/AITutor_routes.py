import os
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import google.generativeai as genai
import subprocess

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

router = APIRouter()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Or the correct model name
    generation_config=generation_config,
    system_instruction="You are an expert Python programming tutor designed to help students learn the basics of Python. When a student asks a Python-related question, you should:\n\n1. **Provide a clear and concise explanation:** Explain the concept in a way that is easy for beginners to understand. Use examples and analogies where appropriate. Break down complex topics into smaller, manageable parts.\n\n2. **Generate three different types of questions in JSON format:** Create questions that test the student's understanding of the explained concept. These questions should be diverse and cover different aspects of the topic. The JSON should be a valid JSON array of objects, where each object represents a question and has the following structure:\n\n```json[\n  {\n    \"type\": \"MCQ\",\n    \"question\": \"The question text for a Multiple Choice Question\",\n    \"options\": {\n      \"A\": \"Option A\",\n      \"B\": \"Option B\",\n      \"C\": \"Option C\",\n      \"D\": \"Option D\"\n    },\n    \"answer\": \"The correct option (A, B, C, or D)\",\n    \"explanation\": \"Explanation of why the answer is correct and why other options are incorrect (if applicable).\"\n  },\n  {\n    \"type\": \"Fill in the Blank\",\n    \"question\": \"The question text with a blank space (e.g., 'The capital of France is ______.')\",\n    \"answer\": \"The correct answer to fill in the blank\",\n    \"explanation\": \"Explanation related to the answer.\"\n  },\n  {\n    \"type\": \"Coding Question\",\n    \"question\": \"The coding question text. Describe the task.\",\n    \"example_input\": {\n      \"input_name_1\": \"Example input value 1\",\n      \"input_name_2\": \"Example input value 2\"\n      // ... more inputs as needed\n    },\n    \"expected_output\": \"The expected output of the code given the example input.\",\n    \"solution\": \"A working Python solution to the coding question. Include comments to explain the code.\",\n    \"explanation\": \"Explanation of the code and how it solves the problem.\"\n  }\n]\n```",
    tools=['code_execution'],  # If you intend to use code execution with Gemini
)


@router.post("/chat")
async def ask_gemini(request: Request):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="Missing 'question' in request body")

        history = data.get("history", [])
        chat_session = model.start_chat(history=history)

        response = chat_session.send_message(question)

        try:
            json_response = json.loads(response.text)  # Attempt JSON parsing
        except json.JSONDecodeError:
            json_response = {"response": response.text, "questions": []} # Provide a default for questions

        json_response['history'] = history + [{"role": "user", "parts": [question]}, {"role": "model", "parts": [response.text]}]

        return JSONResponse(content=json_response)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/runcode")
async def run_code(request: Request):
    try:
        data = await request.json()
        code = data.get('code')

        if not code:
            raise HTTPException(status_code=400, detail="Code is required")

        process = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=10)

        if process.returncode != 0:
            return JSONResponse(status_code=400, content={"detail": process.stderr}) # Return JSON error

        output = process.stdout
        return {"output": output}

    except subprocess.TimeoutExpired:
        return JSONResponse(status_code=400, content={"detail": "Timeout"}) # Return JSON error
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)}) # Return JSON error