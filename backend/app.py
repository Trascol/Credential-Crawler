from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import psycopg2
import os
import sys
import tempfile
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

# backend scripts
from resume_parser import parse_resume
from skill_analysis import find_field, extract_skills

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
bcrypt = Bcrypt(app)

# JWT Secret Key
app.config["JWT_SECRET_KEY"] = "supersecretkey" 
jwt = JWTManager(app)

# Database connection
conn = None
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crawlers:bpz181nyvAckbsUJZ4bq4Vt9q1QYm3IQ@dpg-cul6445ds78s73f5i3jg-a.oregon-postgres.render.com/resume_proj_db")
def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    full_name = data["full_name"]
    password = data["password"]

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s)", 
                            (email, password_hash, full_name))
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, password_hash, full_name FROM users WHERE email = %s", (email,))
                user = cur.fetchone()

        if user and bcrypt.check_password_hash(user[1], password):
            access_token = create_access_token(identity=str(user[0]))
            
            # # For debugging,.. this is painful
            # print("Login response data:", {
            #     "token": access_token,
            #     "name": user[2],
            #     "user_id": user[0]
            # })
            
            return jsonify({"token": access_token, "name": user[2], "user_id": user[0]}), 200

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/get-fields", methods=["GET"])
def get_fields():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM fields ORDER BY popularity DESC")
            rows = cur.fetchall()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/get-skills", methods=["GET"])
def get_skills():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM skills ORDER BY name ASC")
            rows = cur.fetchall()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows]), 200
    except Exception as e:
        print("Error in /get-skills:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/add-field", methods=["POST"])
def add_field():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing field name"}), 400

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO fields (name) VALUES (%s)
                ON CONFLICT (name) DO NOTHING
            """, (name,))
            conn.commit()
        return jsonify({"message": "Field added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/get-latest-resume/<int:user_id>", methods=["GET"])
def get_latest_resume(user_id):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get resume
            cur.execute("SELECT content FROM resumes WHERE user_id = %s", (user_id,))
            resume_row = cur.fetchone()
            if not resume_row:
                return jsonify({"message": "No resume found"}), 404

            # Get skills
            cur.execute("""
                SELECT s.name
                FROM resume_skills rs
                JOIN skills s ON rs.skill_id = s.id
                WHERE rs.resume_id = %s
            """, (user_id,))
            skills = [{"name": row[0]} for row in cur.fetchall()]

            # Guess field
            guessed_field = find_field([s["name"] for s in skills])

        return jsonify({
            "skills_found": skills,
            "guessed_field": guessed_field
        }), 200

    except Exception as e:
        print("Error fetching latest resume:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    file = request.files.get("myfile")
    field_id = request.form.get("field_id")

    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400
    
    if not file or not field_id:
        return jsonify({"error": "Missing file or field selection"}), 400

    try:
        # Parse resume text + extract skills
        resume_data = parse_resume(file, file_type="pdf")
        resume_skills = set(resume_data["skills"])  # Already lowercased

        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                
                text = resume_data["raw_text"]  # You'll need to add this return to your `parse_resume()` function
                parsed_at = datetime.now()
                
                try:
                    # Step 1: Delete old skills associated with this user's resume
                    cur.execute("DELETE FROM resume_skills WHERE resume_id = %s", (user_id,))

                    # Step 2: Insert or update the resume (resume_id = user_id)
                    cur.execute("""
                        INSERT INTO resumes (user_id, content, parsed_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            parsed_at = EXCLUDED.parsed_at
                        RETURNING user_id
                    """, (user_id, text, parsed_at))

                    resume_id = cur.fetchone()[0]

                except Exception as insert_error:
                    print("Resume insert error:", insert_error)

                
                # Bump field popularity
                cur.execute("UPDATE fields SET popularity = popularity + 1 WHERE id = %s", (field_id,))

                # Get all skills in DB
                cur.execute("SELECT id, name FROM skills")
                all_skills = {row[1].lower().strip(): row[0] for row in cur.fetchall()}  # name → id

                # Adding skills to resume_skills table
                for skill in resume_skills:
                    skill_id = all_skills.get(skill)
                    if skill_id:
                        # Insert newly found skills for this resume
                        for skill in resume_skills:
                            skill_id = all_skills.get(skill)
                            if skill_id:
                                cur.execute("""
                                    INSERT INTO resume_skills (resume_id, skill_id, confidence)
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (resume_id, skill_id) DO NOTHING
                                """, (user_id, skill_id, 1.0))
                
                # Get the selected field name
                cur.execute("SELECT name FROM fields WHERE id = %s", (field_id,))
                selected_field_name = cur.fetchone()[0]
                
                # Get skills for the chosen field with importance
                cur.execute("""
                    SELECT s.name, fs.importance
                    FROM field_skills fs
                    JOIN skills s ON s.id = fs.skill_id
                    WHERE fs.field_id = %s
                    ORDER BY fs.importance DESC
                """, (field_id,))
                field_skills_with_importance = [(row[0].lower().strip(), row[1]) for row in cur.fetchall()]
                field_skill_names = {name for name, _ in field_skills_with_importance}

                # Determine matches and extras
                matched_skills = resume_skills.intersection(field_skill_names)
                valid_resume_skills = resume_skills.intersection(all_skills.keys())
                extra_skills = valid_resume_skills - field_skill_names

                missing_skills = [
                    name for name, _ in field_skills_with_importance
                    if name not in resume_skills
                ]
                
                guessed_field = find_field(resume_data["skills"])
                
                # Bump importance of matched field_skills
                for skill in matched_skills:
                    skill_id = all_skills.get(skill)
                    if skill_id:
                        cur.execute("""
                            UPDATE field_skills
                            SET importance = importance + 1
                            WHERE field_id = %s AND skill_id = %s
                        """, (field_id, skill_id))

            return jsonify({ # This is what we're gonna return to the next page. Add here as needed for the info
                "message": "Resume uploaded",
                "field_id": field_id,
                "skills_found": [
                    {"name": name, "importance": importance}
                    for name, importance in field_skills_with_importance
                    if name in matched_skills
                ],
                "max_importance": max([imp for _, imp in field_skills_with_importance] or [1]),
                "other_resume_skills": list(extra_skills),
                "selected_field_name": selected_field_name,
                "guessed_field": guessed_field,
                "missing_skills": missing_skills
            }), 200


    except Exception as e:
        print("Error during upload-resume:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/evaluate-resume-against-job/<int:user_id>/<int:job_id>", methods=["GET"])
def evaluate_resume_against_job(user_id, job_id):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get the latest resume for this user
            cur.execute("SELECT content FROM resumes WHERE user_id = %s", (user_id,))
            resume = cur.fetchone()
            if not resume:
                return jsonify({"error": "No resume found for this user."}), 404

            resume_text = resume[0]
            resume_data = extract_skills(resume_text)
            resume_skills = set(skill.lower().strip() for skill in resume_data)

            # Get job details
            cur.execute("SELECT field_id, job_description FROM job_listings WHERE id = %s", (job_id,))
            job = cur.fetchone()
            if not job:
                return jsonify({"error": "Job listing not found."}), 404

            field_id, job_description = job

            # Get job field name
            cur.execute("SELECT name FROM fields WHERE id = %s", (field_id,))
            job_field_name = cur.fetchone()[0]

            # Get all skills for this field
            cur.execute("""
                SELECT s.name
                FROM field_skills fs
                JOIN skills s ON s.id = fs.skill_id
                WHERE fs.field_id = %s
            """, (field_id,))
            field_skills = set(row[0].lower().strip() for row in cur.fetchall())

            # Extract skills from job_description
            job_skills = extract_skills(job_description)
            job_skills = set(skill.lower().strip() for skill in job_skills)

            all_required_skills = field_skills.union(job_skills)
            matched = resume_skills.intersection(all_required_skills)
            missing = all_required_skills - resume_skills

            # Placeholder field guessing logic (replace with real function)
            guessed_field = "Software Engineer"  # TODO: replace with find_field(resume_text)
            field_match = guessed_field.lower() == job_field_name.lower()

            return jsonify({
                "matched_skills": list(matched),
                "missing_skills": list(missing),
                "resume_field": guessed_field,
                "job_field": job_field_name,
                "field_match": field_match
            }), 200

    except Exception as e:
        print("Evaluation error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
@app.route("/submit-job", methods=["POST"])
def submit_job():
    data = request.json

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO job_listings (
                    company_name, state, city, job_title, job_description,
                    required_qualifications, preferred_qualifications, salary,
                    benefits, work_setting, application_link, field_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["CompanyName"],
                data["CompanyState"],
                data["CompanyCity"],
                data["JobTitle"],
                data["JobDescription"],
                data["RequiredQualifications"],
                data.get("PreferredQualifications", ""),
                data["JobSalary"],
                data.get("benefits", []),
                data["worksetting"],
                data["ApplicationLink"],
                data["field_id"]
            ))
            conn.commit()

        return jsonify({"message": "Job listing submitted!"}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify({"message": "You are accessing a protected route!"})

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/get-jobs", methods=["GET"])
def get_jobs():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    jl.id,
                    jl.company_name,
                    jl.state,
                    jl.city,
                    jl.job_title,
                    jl.salary,
                    jl.job_description,
                    jl.required_qualifications,
                    jl.preferred_qualifications,
                    jl.benefits,
                    jl.work_setting,
                    jl.application_link,
                    jl.posted_at,
                    f.name AS field_name
                FROM job_listings jl
                LEFT JOIN fields f ON jl.field_id = f.id
                ORDER BY jl.posted_at DESC
            """)
            rows = cur.fetchall()

        jobs = []
        for r in rows:
            jobs.append({
                "id": r[0],
                "company_name": r[1],
                "state": r[2],
                "city": r[3],
                "job_title": r[4],
                "salary": r[5],
                "job_description": r[6],
                "required_qualifications": r[7],
                "preferred_qualifications": r[8],
                "benefits": r[9],
                "work_setting": r[10],
                "application_link": r[11],
                "posted_at": r[12],
                "field_name": r[13],
            })

        return jsonify(jobs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/add-skill", methods=["POST"])
def add_skill():
    data = request.json
    skill_name = data.get("name")
    if not skill_name:
        return jsonify({"error": "Missing skill name"}), 400

    # Normalize the skill name (lowercase + stripped)
    normalized_skill = skill_name.lower().strip()
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                # Try inserting the new skill.
                cur.execute("""
                    INSERT INTO skills (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (normalized_skill,))
                result = cur.fetchone()

                # If the skill already exists, retrieve its id.
                if result:
                    skill_id = result[0]
                else:
                    cur.execute("SELECT id FROM skills WHERE name = %s", (normalized_skill,))
                    skill_id = cur.fetchone()[0]

        return jsonify({"message": "Skill added", "skill": {"id": skill_id, "name": normalized_skill}}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/update-field-skills", methods=["POST"])
def update_field_skills():
    file = request.files.get("myfile")
    field_id = request.form.get("field_id")
    if not file or not field_id:
        return jsonify({"error": "Missing file or field selection"}), 400

    try:
        # Parse the resume and get a list/dictionary of skills.
        resume_data = parse_resume(file, file_type="pdf")
        # Normalize each skill for consistency
        resume_skills = set(skill.lower().strip() for skill in resume_data.get("skills", []))

        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                # Update the popularity counter for the field
                cur.execute("UPDATE fields SET popularity = popularity + 1 WHERE id = %s", (field_id,))

                # Retrieve all skills that already exist in the skills table as a mapping: normalized name → id
                cur.execute("SELECT id, name FROM skills")
                all_skills = {row[1].lower().strip(): row[0] for row in cur.fetchall()}

                # Determine which resume skills are new to the skills table.
                new_skills = resume_skills - set(all_skills.keys())
                for skill in new_skills:
                    cur.execute("""
                        INSERT INTO skills (name)
                        VALUES (%s)
                        ON CONFLICT (name) DO NOTHING
                        RETURNING id
                    """, (skill,))
                    result = cur.fetchone()
                    if result:
                        skill_id = result[0]
                    else:
                        # If the insert did nothing, select the id of the existing skill.
                        cur.execute("SELECT id FROM skills WHERE name = %s", (skill,))
                        skill_id = cur.fetchone()[0]
                    # Update our mapping with the newly inserted skill.
                    all_skills[skill] = skill_id

                # Retrieve the skills currently associated with the selected field.
                cur.execute("""
                    SELECT s.name, fs.importance
                    FROM field_skills fs
                    JOIN skills s ON s.id = fs.skill_id
                    WHERE fs.field_id = %s
                    ORDER BY fs.importance DESC
                """, (field_id,))
                field_skills_with_importance = [(row[0].lower().strip(), row[1]) for row in cur.fetchall()]
                field_skill_names = {name for name, _ in field_skills_with_importance}

                # At this point, all resume skills exist in the 'all_skills' mapping.
                valid_resume_skills = resume_skills

                # Skills from the resume already correlated with the field
                matched_skills = valid_resume_skills.intersection(field_skill_names)
                # Skills present in the resume (and the skills table) that are new to the field correlation
                extra_skills = valid_resume_skills - field_skill_names

                # For each skill that is already associated with the field, bump its importance.
                for skill in matched_skills:
                    skill_id = all_skills[skill]
                    cur.execute("""
                        UPDATE field_skills
                        SET importance = importance + 1
                        WHERE field_id = %s AND skill_id = %s
                    """, (field_id, skill_id))

                # For each new skill, insert a new record into field_skills with an initial importance of 1.
                for skill in extra_skills:
                    skill_id = all_skills[skill]
                    cur.execute("""
                        INSERT INTO field_skills (field_id, skill_id, importance)
                        VALUES (%s, %s, 1)
                        ON CONFLICT (field_id, skill_id) DO NOTHING
                    """, (field_id, skill_id))

                # Optionally, refresh the list of updated correlations
                cur.execute("""
                    SELECT s.name, fs.importance
                    FROM field_skills fs
                    JOIN skills s ON s.id = fs.skill_id
                    WHERE fs.field_id = %s
                    ORDER BY fs.importance DESC
                """, (field_id,))
                updated_field_skills = [(row[0].lower().strip(), row[1]) for row in cur.fetchall()]

        return jsonify({
            "message": "Field-skill correlations updated successfully.",
            "updated_skills": [
                {"name": name, "importance": imp}
                for name, imp in updated_field_skills
                if name in valid_resume_skills
            ],
            "new_associations": list(extra_skills),
            "bumped_skills": list(matched_skills)
        }), 200

    except Exception as e:
        print("Error during update-field-skills:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/batch-evaluate", methods=["POST"])
def batch_evaluate():
    # Retrieve multiple resume files and parameters from the form data.
    resume_files = request.files.getlist("myfiles")
    field_id = request.form.get("field_id")
    # The 'selected_skills' field contains comma‐separated skill names.
    selected_skills_str = request.form.get("selected_skills", "")
    
    # We need at least one selection (either a field_id or selected_skills).
    if not resume_files or (not field_id and not selected_skills_str):
        return jsonify({"error": "Missing resume files and at least one selection parameter (field_id or skills)"}), 400

    try:
        required_skills = {}
        # Retrieve field-based skills if a field is provided.
        if field_id:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.name, fs.importance
                    FROM field_skills fs
                    JOIN skills s ON s.id = fs.skill_id
                    WHERE fs.field_id = %s
                """, (field_id,))
                # Create a mapping of the field’s skills (normalized to lowercase).
                field_skills = {row[0].lower().strip(): row[1] for row in cur.fetchall()}
            conn.close()
            required_skills.update(field_skills)

        # Parse manually selected skills (if provided).
        if selected_skills_str:
            manual_skills = [skill.strip().lower() for skill in selected_skills_str.split(",") if skill.strip()]
            for skill in manual_skills:
                # If not already added, add with a default importance of 1.
                if skill not in required_skills:
                    required_skills[skill] = 1

        results = []
        for file in resume_files:
            resume_data = parse_resume(file, file_type="pdf")
            resume_skills = set(skill.lower().strip() for skill in resume_data.get("skills", []))
            matched_skills = resume_skills.intersection(required_skills.keys())
            missing_skills = set(required_skills.keys()) - resume_skills
            score = sum(required_skills[skill] for skill in matched_skills)
            results.append({
                "resume_name": file.filename,
                "matched_skills": list(matched_skills),
                "missing_skills": list(missing_skills),
                "score": score
            })

        # Sort resumes by descending score (most applicable first)
        results.sort(key=lambda x: x["score"], reverse=True)

        return jsonify({"resumes": results}), 200

    except Exception as e:
        print("Error in batch_evaluate:", e)
        return jsonify({"error": str(e)}), 500
