import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import fitz  # PyMuPDF for PDF parsing
import docx  # For DOCX parsing
from typing import Optional
import os
import requests

# Initialize FastAPI
app = FastAPI()

# Set up SQLite database
conn = sqlite3.connect("ai_agent.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don’t exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    experience TEXT,
    skills TEXT,
    additional_info TEXT
)
""")
conn.commit()

//HUGGINGFACE_API_KEY = ""
MODEL_NAME = "tiiuae/falcon-7b-instruct" 
HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

class UploadResumeRequest(BaseModel):
    user_id: str
    file_path: str


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_resume_data(text: str) -> dict:
    data = {
        "name": "",
        "experience": "",
        "skills": "",
        "additional_info": ""
    }
    lines = text.split("\n")
    if lines:
        data["name"] = lines[0].strip()
    for i, line in enumerate(lines):
        if "skills:" in line.lower():
            data["skills"] = lines[i + 1].strip()
    for i, line in enumerate(lines):
        if "experience:" in line.lower():
            data["experience"] = lines[i + 1].strip()
    return data


def generate_response(user_context: str, question: str) -> str:
    prompt = f"You are an AI assistant trained on {user_context}. Answer the following question: {question}"
    payload = {"inputs": prompt}
    
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        raise HTTPException(status_code=response.status_code, detail="Error in AI response")


@app.post("/upload_resume")
def upload_resume(user_id: str, file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    resume_data = parse_resume_data(text)
    cursor.execute("REPLACE INTO user_data VALUES (?, ?, ?, ?, ?)",
                   (user_id, resume_data["name"], resume_data["experience"], resume_data["skills"], resume_data["additional_info"]))
    conn.commit()
    return {"message": "Resume uploaded and parsed successfully"}


@app.get("/ask")
def ask_ai(user_id: str, question: str):
    cursor.execute("SELECT * FROM user_data WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_context = f"Name: {user[1]}, Experience: {user[2]}, Skills: {user[3]}, Additional Info: {user[4]}"
    return {"response": generate_response(user_context, question)}


@app.post("/add_user")
def add_user(user_id: str, name: str, experience: str, skills: str, additional_info: Optional[str] = ""):
    cursor.execute("REPLACE INTO user_data VALUES (?, ?, ?, ?, ?)",
                   (user_id, name, experience, skills, additional_info))
    conn.commit()
    return {"message": "User data added successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
