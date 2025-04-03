from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import psycopg2
import os

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
            cur.execute("SELECT id, name FROM fields ORDER BY name ASC")
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
