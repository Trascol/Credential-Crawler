"""This script is used to parse through a users resume to retrieve name, contact information, and skills found on resume."""

# pip install pdfminer.six python-docx spacy nltk
# python -m spacy download en_core_web_sm

import re
import spacy
from pdfminer.high_level import extract_text
from skill_analysis import find_field, extract_skills
from docx import Document

nlp = spacy.load("en_core_web_sm") # Web assuming

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_contact_info(text):
    email_pattern = r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+"
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    
    email = re.findall(email_pattern, text)
    phone = re.findall(phone_pattern, text)
    
    return {"email": email, "phone": phone}

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def parse_resume(file_path, file_type="pdf"):
    if file_type == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

    parsed_data = {
        "name": extract_name(text),
        "contact_info": extract_contact_info(text),
        "skills": extract_skills(text)
    }
    
    return parsed_data

if __name__ == "__main__":

    file_path = "resume.pdf"  # Get users pdf and locally store it maybe? Then delete the actual pdf after its parsed
    resume_data = parse_resume(file_path, file_type="pdf") # I wanna stick with pdf
    
    user_name = resume_data.get("name")
    user_email = resume_data.get("contact_info", {}).get("email", [])
    user_phone = resume_data.get("contact_info", {}).get("phone", [])
    user_skills = resume_data.get("skills")
    
    print("\n")
    print(f"Name: {user_name}")
    print(f"Email: {user_email}")
    print(f"Phone number: {user_phone}")
    print(f"Skills: {user_skills}")
    
    assumed_field = find_field(user_skills)
    
    print(f"\nMost likely field: {assumed_field}")
