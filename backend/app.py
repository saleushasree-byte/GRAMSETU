
from flask import Flask, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sqlite3
import os

from agriculture import get_agriculture_advice

app = Flask(__name__)

app.secret_key = os.environ.get(
    "GRAMSETU_SECRET_KEY",
    "dev-only-change-this-secret-before-deployment"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

CORS(
    app,
    origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    supports_credentials=True
)


# --------------------------------
# DATABASE INITIALIZATION
# --------------------------------


def init_database():

    os.makedirs("data", exist_ok=True)

    connection = sqlite3.connect("data/gramsetu.db")
    cursor = connection.cursor()

    # Existing farmer profile table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmer_profile (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL
        )
    """)

    # User registration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            state TEXT,
            district TEXT,
            village TEXT
        )
    """)

    # Upgrade existing users table if columns are missing
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    for column in ["email", "state", "district", "village"]:
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE users ADD COLUMN {column} TEXT"
            )

    connection.commit()
    connection.close()


init_database()



# --------------------------------
# HOME API
# --------------------------------

@app.route("/")
def home():

    return "Welcome to GRAMSETU Backend!"


# --------------------------------
# HEALTH API
# --------------------------------

@app.route("/api/health")
def health():

    return {
        "status": "success",
        "message": "GRAMSETU backend is running"
    }


# --------------------------------
# ABOUT API
# --------------------------------

@app.route("/api/about")
def about():

    return {
        "project": "GRAMSETU",
        "description": "AI-driven rural development platform"
    }


# --------------------------------
# TEST API
# --------------------------------

@app.route("/api/test", methods=["POST"])
def test():

    data = request.get_json(silent=True)

    if data is None or "name" not in data:
        return {
            "status": "error",
            "message": "Name is required"
        }, 400

    name = data["name"]

    return {
        "message": f"Hello {name}!"
    }


# --------------------------------
# AGRICULTURE API
# --------------------------------

@app.route("/api/agriculture/advice", methods=["POST"])
def agriculture_advice():

    data = request.get_json(silent=True)

    if data is None:
        return {
            "status": "error",
            "message": "Invalid JSON data"
        }, 400

    crop = data.get("crop")
    soil = data.get("soil")

    if not crop or not soil:
        return {
            "status": "error",
            "message": "Crop and soil are required"
        }, 400

    advice = get_agriculture_advice(crop, soil)

    return {
        "status": "success",
        "crop": crop,
        "soil": soil,
        "advice": advice
    }


# --------------------------------
# SCHEMES API
# --------------------------------

@app.route("/api/schemes", methods=["GET"])
def schemes():

    with open("data/schemes.json", "r", encoding="utf-8") as file:
        schemes_data = json.load(file)

    category = request.args.get("category")
    search = request.args.get("search")

    if category:

        schemes_data = [
            scheme
            for scheme in schemes_data
            if scheme["category"].lower() == category.lower()
        ]

    if search:

        schemes_data = [
            scheme
            for scheme in schemes_data
            if search.lower() in scheme["name"].lower()
            or search.lower() in scheme["description"].lower()
            or search.lower() in scheme["category"].lower()
        ]

    return {
        "status": "success",
        "count": len(schemes_data),
        "schemes": schemes_data
    }


# --------------------------------
# SCHEME CATEGORIES API
# --------------------------------

@app.route("/api/schemes/categories", methods=["GET"])
def scheme_categories():

    with open("data/schemes.json", "r", encoding="utf-8") as file:
        schemes_data = json.load(file)

    categories = sorted(
        set(
            scheme["category"]
            for scheme in schemes_data
        )
    )

    return {
        "status": "success",
        "categories": categories
    }


# --------------------------------
# ELIGIBLE SCHEMES API
# --------------------------------

@app.route("/api/schemes/eligible", methods=["GET"])
def eligible_schemes():

    category = request.args.get("category")

    if not category:
        return {
            "status": "error",
            "message": "Category is required"
        }, 400

    with open("data/schemes.json", "r", encoding="utf-8") as file:
        schemes_data = json.load(file)

    eligible = [
        scheme
        for scheme in schemes_data
        if scheme["category"].lower() == category.lower()
    ]

    return {
        "status": "success",
        "count": len(eligible),
        "eligible_schemes": eligible
    }


# --------------------------------
# SCHEME DETAILS API
# --------------------------------

@app.route("/api/schemes/<scheme_name>", methods=["GET"])
def scheme_details(scheme_name):

    with open("data/schemes.json", "r", encoding="utf-8") as file:
        schemes_data = json.load(file)

    for scheme in schemes_data:

        if scheme["name"].lower() == scheme_name.lower():

            return {
                "status": "success",
                "scheme": scheme
            }

    return {
        "status": "error",
        "message": "Scheme not found"
    }, 404


# --------------------------------
# CROPS API
# --------------------------------

@app.route("/api/crops", methods=["GET"])
def crops():

    with open("data/crops.json", "r", encoding="utf-8") as file:
        crops_data = json.load(file)

    return {
        "status": "success",
        "crops": crops_data
    }


# --------------------------------
# FARMER PROFILE - CREATE
# --------------------------------

@app.route("/api/farmer/profile", methods=["POST"])
def farmer_profile():

    data = request.get_json(silent=True)

    if data is None:
        return {
            "status": "error",
            "message": "Invalid JSON data"
        }, 400

    name = data.get("name")
    age = data.get("age")
    state = data.get("state")
    district = data.get("district")

    if not name or not age or not state or not district:
        return {
            "status": "error",
            "message": "Name, age, state and district are required"
        }, 400

    connection = sqlite3.connect("data/gramsetu.db")

    cursor = connection.cursor()

    cursor.execute("DELETE FROM farmer_profile")

    cursor.execute("""
        INSERT INTO farmer_profile
        (id, name, age, state, district)
        VALUES (?, ?, ?, ?, ?)
    """, (
        1,
        name,
        age,
        state,
        district
    ))

    connection.commit()
    connection.close()

    farmer = {
        "name": name,
        "age": age,
        "state": state,
        "district": district
    }

    return {
        "status": "success",
        "message": "Farmer profile saved successfully",
        "farmer": farmer
    }, 201


# --------------------------------
# FARMER PROFILE - GET
# --------------------------------

@app.route("/api/farmer/profile", methods=["GET"])
def get_farmer_profile():

    connection = sqlite3.connect("data/gramsetu.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, age, state, district
        FROM farmer_profile
        WHERE id = 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return {
            "status": "error",
            "message": "Farmer profile not found"
        }, 404

    farmer = {
        "name": row[0],
        "age": row[1],
        "state": row[2],
        "district": row[3]
    }

    return {
        "status": "success",
        "farmer": farmer
    }


# --------------------------------
# FARMER PROFILE - UPDATE
# --------------------------------

@app.route("/api/farmer/profile", methods=["PUT"])
def update_farmer_profile():

    data = request.get_json(silent=True)

    if data is None:
        return {
            "status": "error",
            "message": "Invalid JSON data"
        }, 400

    name = data.get("name")
    age = data.get("age")
    state = data.get("state")
    district = data.get("district")

    if not name or not age or not state or not district:
        return {
            "status": "error",
            "message": "Name, age, state and district are required"
        }, 400

    connection = sqlite3.connect("data/gramsetu.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM farmer_profile
        WHERE id = 1
    """)

    row = cursor.fetchone()

    if row is None:

        connection.close()

        return {
            "status": "error",
            "message": "Farmer profile not found"
        }, 404

    cursor.execute("""
        UPDATE farmer_profile
        SET name = ?,
            age = ?,
            state = ?,
            district = ?
        WHERE id = 1
    """, (
        name,
        age,
        state,
        district
    ))

    connection.commit()
    connection.close()

    farmer = {
        "name": name,
        "age": age,
        "state": state,
        "district": district
    }

    return {
        "status": "success",
        "message": "Farmer profile updated successfully",
        "farmer": farmer
    }


# --------------------------------
# FARMER PROFILE - DELETE
# --------------------------------

@app.route("/api/farmer/profile", methods=["DELETE"])
def delete_farmer_profile():

    connection = sqlite3.connect("data/gramsetu.db")

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM farmer_profile
        WHERE id = 1
    """)

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted == 0:

        return {
            "status": "error",
            "message": "Farmer profile not found"
        }, 404

    return {
        "status": "success",
        "message": "Farmer profile deleted successfully"
    }


# --------------------------------
# COMPLAINTS API - CREATE
# --------------------------------

@app.route("/api/complaints", methods=["POST"])
def create_complaint():

    with open("data/complaints.json", "r", encoding="utf-8") as file:
        complaints = json.load(file)

    data = request.get_json(silent=True)

    if data is None:
        return {
            "status": "error",
            "message": "Invalid JSON data"
        }, 400

    name = data.get("name")
    village = data.get("village")
    category = data.get("category")
    description = data.get("description")

    if not name or not village or not category or not description:
        return {
            "status": "error",
            "message": "Name, village, category and description are required"
        }, 400

    if complaints:

        new_id = max(
            complaint["id"]
            for complaint in complaints
        ) + 1

    else:

        new_id = 1

    complaint = {
        "id": new_id,
        "name": name,
        "village": village,
        "category": category,
        "description": description,
        "status": "Pending"
    }

    complaints.append(complaint)

    with open("data/complaints.json", "w", encoding="utf-8") as file:
        json.dump(
            complaints,
            file,
            indent=4,
            ensure_ascii=False
        )

    return {
        "status": "success",
        "message": "Complaint submitted successfully",
        "complaint": complaint
    }, 201


# --------------------------------
# COMPLAINTS API - GET ALL
# --------------------------------

@app.route("/api/complaints", methods=["GET"])
def get_complaints():

    with open("data/complaints.json", "r", encoding="utf-8") as file:
        complaints = json.load(file)

    return {
        "status": "success",
        "count": len(complaints),
        "complaints": complaints
    }


# --------------------------------
# GET COMPLAINT BY ID
# --------------------------------

@app.route("/api/complaints/<int:complaint_id>", methods=["GET"])
def get_complaint_by_id(complaint_id):

    with open("data/complaints.json", "r", encoding="utf-8") as file:
        complaints = json.load(file)

    for complaint in complaints:

        if complaint["id"] == complaint_id:

            return {
                "status": "success",
                "complaint": complaint
            }

    return {
        "status": "error",
        "message": "Complaint not found"
    }, 404


# --------------------------------
# UPDATE COMPLAINT
# --------------------------------

@app.route("/api/complaints/<int:complaint_id>", methods=["PUT"])
def update_complaint(complaint_id):

    with open("data/complaints.json", "r", encoding="utf-8") as file:
        complaints = json.load(file)

    data = request.get_json(silent=True)

    if data is None:
        return {
            "status": "error",
            "message": "Invalid JSON data"
        }, 400

    for complaint in complaints:

        if complaint["id"] == complaint_id:

            if data.get("status"):
                complaint["status"] = data.get("status")

            if data.get("description"):
                complaint["description"] = data.get("description")

            with open("data/complaints.json", "w", encoding="utf-8") as file:
                json.dump(
                    complaints,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return {
                "status": "success",
                "message": "Complaint updated successfully",
                "complaint": complaint
            }

    return {
        "status": "error",
        "message": "Complaint not found"
    }, 404


# --------------------------------
# DELETE COMPLAINT
# --------------------------------

@app.route("/api/complaints/<int:complaint_id>", methods=["DELETE"])
def delete_complaint(complaint_id):

    with open("data/complaints.json", "r", encoding="utf-8") as file:
        complaints = json.load(file)

    for complaint in complaints:

        if complaint["id"] == complaint_id:

            complaints.remove(complaint)

            with open("data/complaints.json", "w", encoding="utf-8") as file:
                json.dump(
                    complaints,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return {
                "status": "success",
                "message": "Complaint deleted successfully"
            }

    return {
        "status": "error",
        "message": "Complaint not found"
    }, 404


# --------------------------------
# DASHBOARD API
# --------------------------------

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    with open("data/schemes.json", "r", encoding="utf-8") as file:
        schemes_data = json.load(file)

    with open("data/crops.json", "r", encoding="utf-8") as file:
        crops_data = json.load(file)

    with open("data/complaints.json", "r", encoding="utf-8") as file:
        complaints_data = json.load(file)

    return {
        "status": "success",
        "project": "GRAMSETU",
        "total_schemes": len(schemes_data),
        "total_crops": len(crops_data),
        "total_complaints": len(complaints_data)
    }


# --------------------------------
# 404 ERROR HANDLER
# --------------------------------

@app.errorhandler(404)
def not_found(error):

    return {
        "status": "error",
        "message": "API endpoint not found"
    }, 404


# --------------------------------
# START SERVER
# --------------------------------

# --------------------------------
# USER REGISTRATION API
# --------------------------------


@app.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    name = data.get("name", "").strip()
    mobile = data.get("mobile", "").strip()
    password = data.get("password", "")
    email = data.get("email", "").strip()
    state = data.get("state", "").strip()
    district = data.get("district", "").strip()
    village = data.get("village", "").strip()

    if not name or not mobile or not password:
        return {
            "status": "error",
            "message": "All fields are required"
        }, 400

    if len(password) < 8:
        return {
            "status": "error",
            "message": "Password must contain at least 8 characters"
        }, 400

    password_hash = generate_password_hash(password)

    try:
        connection = sqlite3.connect("data/gramsetu.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                name, mobile, password_hash,
                email, state, district, village
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, mobile, password_hash,
            email, state, district, village
        ))

        connection.commit()
        connection.close()

        return {
            "status": "success",
            "message": "Registration successful"
        }, 201

    except sqlite3.IntegrityError:
        return {
            "status": "error",
            "message": "Mobile number already registered"
        }, 409

    except Exception:
        return {
            "status": "error",
            "message": "Registration failed. Please try again."
        }, 500


# --------------------------------
# USER LOGIN API
# --------------------------------

@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    mobile = data.get("mobile", "").strip()
    password = data.get("password", "")

    if not mobile or not password:
        return {
            "status": "error",
            "message": "Mobile number and password are required"
        }, 400

    connection = sqlite3.connect("data/gramsetu.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, mobile, password_hash,
       email, state, district, village
        FROM users
        WHERE mobile = ?
    """, (mobile,))

    user = cursor.fetchone()
    connection.close()

    if user is None or not check_password_hash(user[3], password):
        return {
            "status": "error",
            "message": "Invalid mobile number or password"
        }, 401

    session["user_id"] = user[0]

    return {
        "status": "success",
        "message": "Login successful",
       
"user": {
    "id": user[0],
    "name": user[1],
    "mobile": user[2],
    "email": user[4],
    "state": user[5],
    "district": user[6],
    "village": user[7]
}

    }, 200



# --------------------------------
# CHECK CURRENT USER API
# --------------------------------

@app.route("/api/auth/me", methods=["GET"])
def current_user():

    user_id = session.get("user_id")

    if not user_id:
        return {
            "status": "error",
            "message": "Not logged in"
        }, 401

    connection = sqlite3.connect("data/gramsetu.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, mobile, email, state, district, village
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()
    connection.close()

    if user is None:
        session.clear()
        return {
            "status": "error",
            "message": "User not found"
        }, 401

    return {
        "status": "success",
        
"user": {
    "id": user[0],
    "name": user[1],
    "mobile": user[2],
    "email": user[3],
    "state": user[4],
    "district": user[5],
    "village": user[6]
}

    }, 200


# --------------------------------
# USER LOGOUT API
# --------------------------------

@app.route("/api/auth/logout", methods=["POST"])
def logout():

    session.clear()

    return {
        "status": "success",
        "message": "Logout successful"
    }, 200


if __name__ == "__main__":
    app.run(debug=True)