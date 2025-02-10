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
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Change this in production!
jwt = JWTManager(app)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crawlers:bpz181nyvAckbsUJZ4bq4Vt9q1QYm3IQ@dpg-cul6445ds78s73f5i3jg-a.oregon-postgres.render.com/resume_proj_db")
conn = psycopg2.connect(DATABASE_URL)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    full_name = data["full_name"]
    password = data["password"]

    # Hash password
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s)", 
                        (email, password_hash, full_name))
            conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    with conn.cursor() as cur:
        cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

    if user and bcrypt.check_password_hash(user[1], password):
        access_token = create_access_token(identity=user[0])
        return jsonify({"token": access_token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify({"message": "You are accessing a protected route!"})

if __name__ == "__main__":
    app.run(debug=True)
