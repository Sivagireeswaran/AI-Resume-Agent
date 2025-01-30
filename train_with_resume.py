
import requests
from resume_parser import extract_text_from_pdf, parse_resume_text

def train_ai_with_resume(parsed_data):
    user_data = {
        "user_id": "123",
        "name": parsed_data["name"],
        "experience": parsed_data["experience"],
        "skills": parsed_data["skills"],
        "additional_info": parsed_data.get("additional_info", "")
    }
    response = requests.post("http://localhost:8000/train", json=user_data)
    return response.json()

# Example usage
parsed_data = parse_resume_text(extract_text_from_pdf("D:\SIVA\AIAG\Sivagireeswaran S.pdf"))
print(parsed_data)  # Check parsed data
train_ai_with_resume(parsed_data)
