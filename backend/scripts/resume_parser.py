"""This script is used to parse through a users resume to retrieve name, contact information, and skills found on resume."""

# pip install pdfminer.six python-docx spacy nltk
# python -m spacy download en_core_web_sm

import re
import spacy
from pdfminer.high_level import extract_text
from skill_analysis import find_field, extract_skills, normalize
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

def parse_resume(file, file_type="pdf"):
    if file_type != "pdf":
        raise ValueError("Only PDF format supported.")
    
    text = extract_text(file.stream)

    parsed_data = {
        "name": extract_name(text),
        "contact_info": extract_contact_info(text),
        "skills": extract_skills(text),
        "raw_text": normalize(text)
    }

    return parsed_data
