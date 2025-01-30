import fitz  
import docx
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using PyMuPDF"""
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text("text")
    return text

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_resume_text(text):
    """Parse the resume text to extract structured information"""
    parsed_data = {}

    # Extracting Name (assumes name is first line)
    name_match = re.match(r"^[A-Za-z\s]+$", text.split('\n')[0])  # Matches the first line for name
    parsed_data["name"] = name_match.group(0) if name_match else "Name not found"

    # Extracting Experience (Looking for 'Experience' or 'Work Experience')
    experience_match = re.search(r"(Experience|Work Experience)\s*([\s\S]+?)(Education|Skills|$)", text)
    parsed_data["experience"] = experience_match.group(2).strip() if experience_match else "Experience not found"

    # Extracting Skills
    skills_match = re.search(r"(Technical Skills)\s*([\s\S]+?)(Certifications|Extracurricular|$)", text)
    parsed_data["skills"] = skills_match.group(2).strip() if skills_match else "Skills not found"

    #  Extracting Education (Looking for "Education" section and extracting content after it)
    education_match = re.search(r"(Education|Academic)\s*([\s\S]+?)(Projects|Certifications|Extracurricular|$)", text)
    parsed_data["education"] = education_match.group(2).strip() if education_match else "Education not found"

    # Extracting Projects (Looking for "Projects" section)
    projects_match = re.search(r"(Projects)\s*([\s\S]+?)(Technical Skills|Certifications|Extracurricular|$)", text)
    parsed_data["projects"] = projects_match.group(2).strip() if projects_match else "Projects not found"

        # Extracting Certifications (Looking for "Certifications" section)
    certifications_match = re.search(r"(Certifications)\s*([\s\S]+?)(Extracurricular|$)", text)
    parsed_data["certifications"] = certifications_match.group(2).strip() if certifications_match else "Certifications not found"

    # Extracting Extracurricular (Looking for "Extracurricular" section)
    extracurricular_match = re.search(r"(Extracurricular)\s*([\s\S]+)", text)
    parsed_data["extracurricular"] = extracurricular_match.group(2).strip() if extracurricular_match else "Extracurricular activities not found"

    return parsed_data
