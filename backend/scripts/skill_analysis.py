"""This script will handle extracting skills from resumes or job listings, suggest skills to learn/add, analyze and expose missing skills from a resume"""

#NOTE: Need to pull skills from DB still


import re
import spacy

# Sample skills database (Needs to be replaced with real DB or API connection)
skills_db = {"Python", "Java", "C++", "C#", "JavaScript", "SQL", "Machine Learning", 
             "Deep Learning", "AI", "Django", "Flask", "React", "TensorFlow", "PyTorch"}

nlp = spacy.load("en_core_web_sm") # Web assuming


def skill_suggestion():
    pass

def skill_gap_analysis():
    pass

def find_field(skills): 
    if not skills:  
        return "Unknown Field"

    tech_fields = {
        "Software Engineering": {"python", "java", "c++", "c#", "git"},
        "Data Science": {"python", "sql", "machine learning", "pandas"},
        "Web Development": {"javascript", "html", "css", "react"},
        "Cybersecurity": {"networking", "linux", "penetration testing", "cryptography"}
    }

    skills = {skill.lower() for skill in skills}  # Convert skills to lowercase for case-insensitive matching

    field_scores = {
        field: sum(1 for skill in skills if skill in {s.lower() for s in skill_set})  
        for field, skill_set in tech_fields.items()
    }

    best_field = max(field_scores, key=field_scores.get)
    
    return best_field if field_scores[best_field] > 0 else "Unknown Field"

def extract_skills(text):
    
    """
    Provide text from resume or job listing
    
    returns a list of found skills
    """
    
    # Process the text with spaCy NLP model
    doc = nlp(text)
    detected_skills = set()

    # Extract skills using Named Entity Recognition (NER) but focus on "skills-related" entities
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:  # Remove these broad categories
            continue
        if ent.label_ == "LANGUAGE":  # Add programming languages recognized by spaCy
            detected_skills.add(ent.text.strip())

    # Additional regex-based skill extraction (for exact matches)
    patterns = [
        r"\bC\+\+\b", r"\bC#\b", r"\bPython\b", r"\bJava\b", r"\bJavaScript\b",
        r"\bSQL\b", r"\bMachine Learning\b", r"\bDeep Learning\b", r"\bAI\b",
        r"\bDjango\b", r"\bFlask\b", r"\bReact\b", r"\bTensorFlow\b", r"\bPyTorch\b",
        r"\bAWS\b", r"\bGoogle Sheets\b", r"\bEclipse\b", r"\bApache\b", r"\bGitHub\b"
    ]
    
    # Refined matching for skills (no multi-word matches unless they're exact tech terms)
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        detected_skills.update([match.lower() for match in matches])  # Normalize to lowercase

    # Match against known skills in DB (case insensitive)
    matched_skills = {skill.lower() for skill in skills_db if skill.lower() in text.lower()}

    # Combine all detected skills (remove duplicates and non-relevant items)
    all_skills = detected_skills.union(matched_skills)

    # Optionally filter out non-relevant results (e.g., university names, project names)
    irrelevant_terms = {"university", "project", "tool", "company"}
    all_skills = {skill for skill in all_skills if not any(term in skill.lower() for term in irrelevant_terms)}

    return list(all_skills)

# def extract_skills(text): # Simple parsing, just looking for key words found in resume
#     text = text.lower()

#     skills_db = {"python", "java", "c++", "c", "sql", "machine learning", "ai", "django", "flask", "deep learning"}

#     found_skills = set()

#     for skill in skills_db:
#         # Handle cases where C++ might be written as C/C++
#         skill_pattern = rf'(?<!\w){re.escape(skill)}(?!\w)'
        
#         if re.search(skill_pattern, text, re.IGNORECASE):
#             found_skills.add(skill)

#     return list(found_skills)