# NOTE
# Handles PDFs, txt, and DOCX files resume files, this script will try to parse and populate areas for user in DB.
# Uses regxx

# pip install pdfminer.six python-docx spacy nltk
# python -m spacy download en_core_web_sm

import re
import spacy
from pdfminer.high_level import extract_text
from docx import Document

nlp = spacy.load("en_core_web_sm")

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

def extract_skills(text):
    skills = ["Python", "Java", "C++", "SQL", "Machine Learning", "AI", "Django", "Flask"]  # Dominic we should have it gather a list from the DB this is just proof of concept
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return found_skills

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

def main(): 
    pass

if __name__ == "__main__":
    
    status_code = main()
    
file_path = "resume.pdf"  # Get users pdf and locally store it maybe? Then delete the actual pdf after its parsed
resume_data = parse_resume(file_path, file_type="pdf") # I wanna stick with pdf
print(resume_data)
