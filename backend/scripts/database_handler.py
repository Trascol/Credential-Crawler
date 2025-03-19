"""This script is used to handle updating and pulling data from/to the database for all python scripts"""

#NOTE: NEED TO UPDATE WITH WHAT WE're ACTUALLY USING LOL

import sqlite3

def connect_db(db_name="skills_db.sqlite"):
    conn = sqlite3.connect(db_name)
    return conn

def update_user_skills(user_skills, user_field):
    conn = connect_db()
    cursor = conn.cursor()

    # Update or insert skills for the user
    cursor.executemany("INSERT INTO user_skills (user_id, skill) VALUES (?, ?)", user_skills)

    # Update the field for the user
    cursor.execute("UPDATE users SET field=? WHERE user_id=?", (user_field, user_id))
    conn.commit()
    conn.close()

def get_user_skills(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT skill FROM user_skills WHERE user_id=?", (user_id,))
    skills = [row[0] for row in cursor.fetchall()]
    conn.close()
    return skills

def add_or_update_skills_db(skills, field):
    conn = connect_db()
    cursor = conn.cursor()

    # Add/update skills
    for skill in skills:
        cursor.execute("INSERT OR REPLACE INTO skills (skill_name, field) VALUES (?, ?)", (skill, field))
    
    conn.commit()
    conn.close()
