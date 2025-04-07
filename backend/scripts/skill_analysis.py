"""This script handles extracting skills from resumes, analyzing skill gaps, and suggesting relevant fields."""

import re
import spacy
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables and spaCy model
load_dotenv()
nlp = spacy.load("en_core_web_sm")

# === DB connection ===
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://crawlers:bpz181nyvAckbsUJZ4bq4Vt9q1QYm3IQ@dpg-cul6445ds78s73f5i3jg-a.oregon-postgres.render.com/resume_proj_db"))

# === Skill Extraction ===
def normalize(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def extract_skills(text):
    text = normalize(text)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM skills")
            db_skills = [normalize(row[0]) for row in cur.fetchall()]
    finally:
        conn.close()

    found = set()
    for skill in db_skills:
        # Match whole skill term, e.g., 'visual studio code'
        pattern = re.escape(skill)
        if re.search(rf'\b{pattern}\b', text):
            found.add(skill)

    return list(found)

# === Field Guessing ===
def find_field(skills_from_resume):
    if not skills_from_resume:
        return "Unknown Field"

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get all field-skill relationships
            cur.execute("""
                SELECT f.id, f.name, s.name
                FROM fields f
                JOIN field_skills fs ON fs.field_id = f.id
                JOIN skills s ON s.id = fs.skill_id
            """)
            field_skill_map = {}
            for field_id, field_name, skill_name in cur.fetchall():
                skill_name = skill_name.lower().strip()
                if field_id not in field_skill_map:
                    field_skill_map[field_id] = {
                        "name": field_name,
                        "skills": set()
                    }
                field_skill_map[field_id]["skills"].add(skill_name)

        # Normalize resume skills
        resume_skills = {s.lower().strip() for s in skills_from_resume}

        # Compute overlap scores
        field_scores = {
            fid: len(data["skills"].intersection(resume_skills))
            for fid, data in field_skill_map.items()
        }

        # Find field with highest overlap
        best_field_id = max(field_scores, key=field_scores.get, default=None)
        if best_field_id and field_scores[best_field_id] > 0:
            return field_skill_map[best_field_id]["name"]
        else:
            return "Unknown Field"

    except Exception as e:
        print("Error in find_field:", e)
        return "Unknown Field"


# === TODO placeholders ===
def skill_suggestion():
    pass

def skill_gap_analysis():
    pass
