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

def extract_skills(text): # Returns a list of all skills found based on previously added skills in DB
    # DO A DB FETCH INTO DATA BASE TO LOOK FOR SKILLS HERE
    skills_db = {"Python", "Java", "C++", "SQL", "Machine Learning", "AI", "Django", "Flask", "Deep Learning"}
    
    # Use regex to ensure standalone words/phrases match
    found_skills = {skill for skill in skills_db if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE)}
    
    return list(found_skills)

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

def field_assumptions(skills): # This function is where we can potentially just classifying fields.
    # This is important because maybe based on best_field we can design a new resume for them.
    
    tech_fields = {
        "Software Engineering": {"Python", "Java", "C++", "C#", "Git"},
        "Data Science": {"Python", "SQL", "Machine Learning", "Pandas"},
        "Web Development": {"JavaScript", "HTML", "CSS", "React"},
        "Cybersecurity": {"Networking", "Linux", "Penetration Testing", "Cryptography"}
    }

    field_counts = {field: len(skills.intersection(skill_set)) for field, skill_set in tech_fields.items()}

    best_field = max(field_counts, key=field_counts.get)
    
    return best_field if field_counts[best_field] > 0 else "Unknown Field"

if __name__ == "__main__":

    file_path = "resume.pdf"  # Get users pdf and locally store it maybe? Then delete the actual pdf after its parsed
    resume_data = parse_resume(file_path, file_type="pdf") # I wanna stick with pdf
    print(resume_data)
