import os
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import google.generativeai as genai
import subprocess  # Or use a Docker container for better sandboxing

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

router = APIRouter()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",


}  # Removed response_mime_type as it's handled by FastAPI

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Ensure this model name is correct
    generation_config=generation_config,
    system_instruction="You are an expert Python programming tutor designed to help students learn the basics of Python. When a student asks a Python-related question, you should:\n\n1. **Provide a clear and concise explanation:** Explain the concept in a way that is easy for beginners to understand. Use examples and analogies where appropriate. Break down complex topics into smaller, manageable parts.\n\n2. **Generate three different types of questions:** Create questions that test the student's understanding of the explained concept. These questions should be diverse and cover different aspects of the topic.\n\n * **Multiple Choice Question (MCQ):** Provide 4 options (A, B, C, D) and clearly indicate the correct answer.\n\n * **Fill in the Blank Question:** Present a statement with a blank space and ask the student to fill it in. Provide the correct answer separately.\n\n * **Coding Question:** Give a small coding task related to the concept. Include example input and expected output. Provide a working solution to the coding question separately.\n\n3. **Format the response clearly:** Use markdown formatting to make the response easy to read. Use headings, bullet points, code blocks, and bold text to structure the information.\n\n**Example Interaction:**\n\n**Student Question:** What are variables in Python?\n\n**Your Response:**\n\n## Variables in Python\n\nVariables are like containers that store data in your Python programs. Think of them as labeled boxes where you can put different things. You can store numbers, text, or other types of data in variables.\n\n**Key Concepts:**\n\n* **Naming Variables:** Variable names must follow certain rules (e.g., they can't start with a number, can contain letters, numbers, and underscores).\n* **Assigning Values:** You use the `=` operator to assign a value to a variable.\n* **Data Types:** Variables can hold different data types (e.g., integers, strings, floats, booleans).\n\n**Example:**\n\n```python\nname = \"Alice\" # Stores a string\nage = 30 # Stores an integer\nheight = 5.8 # Stores a float\nis_student = True # Stores a boolean",
    tools=['code_execution'],  # Make sure code_execution is enabled if needed

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
            json_response = json.loads(response.text)
        except json.JSONDecodeError:
            json_response = {"response": response.text} # Or a more appropriate error structure

        json_response['history'] = history + [{"role": "user", "parts": [question]}, {"role": "model", "parts": [response.text]}] # Correctly update history

        return JSONResponse(content=json_response)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    




@router.post("/runcode")
async def run_code(request: Request):  # Use async and Request object
    try:
        data = await request.json()  # Asynchronously get JSON data
        code = data.get('code')

        if not code:
            raise HTTPException(status_code=400, detail="Code is required")


        process = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=10)

        if process.returncode != 0:  # Check for non-zero return code (error)
            raise HTTPException(status_code=400, detail=process.stderr)  # Raise HTTP exception with error

        output = process.stdout
        return {"output": output}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=400, detail="Timeout")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))