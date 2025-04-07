from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import psycopg2
import os
import sys
import tempfile

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
            return jsonify({"token": access_token, "name": user[2]}), 200

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

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    file = request.files.get("myfile")
    field_id = request.form.get("field_id")

    if not file or not field_id:
        return jsonify({"error": "Missing file or field selection"}), 400

    try:
        # Parse resume text + extract skills
        resume_data = parse_resume(file, file_type="pdf")
        resume_skills = set(resume_data["skills"])  # Already lowercased

        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                # Bump field popularity
                cur.execute("UPDATE fields SET popularity = popularity + 1 WHERE id = %s", (field_id,))

                # Get all skills in DB
                cur.execute("SELECT id, name FROM skills")
                all_skills = {row[1].lower().strip(): row[0] for row in cur.fetchall()}  # name → id

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
