from flask import Flask, render_template, request, redirect, send_from_directory, session
import mysql.connector
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import json

# ==============================
# LOAD ENV VARIABLES
# ==============================

load_dotenv()

app = Flask(__name__)

app.secret_key = "civic_ai_secret"

# ==============================
# GEMINI API
# ==============================

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.5-flash")

# ==============================
# MYSQL CONNECTION
# ==============================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="civic_ai"
)

cursor = db.cursor(dictionary=True)

# ==============================
# UPLOAD FOLDER
# ==============================

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():

    return render_template("login.html")

# ==============================
# REGISTER
# ==============================

@app.route("/register", methods=["POST"])
def register():

    try:

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]

        role = request.form["role"]

        # Check Existing User
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return "Email already exists"

        # Insert User
        sql = """
        INSERT INTO users
        (
            name,
            email,
            password,
            role
        )

        VALUES (%s,%s,%s,%s)
        """

        values = (
            name,
            email,
            password,
            role
        )

        cursor.execute(sql, values)

        db.commit()

        return redirect("/")

    except Exception as e:

        return f"Register Error: {str(e)}"

# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login():

    try:

        email = request.form["email"]

        password = request.form["password"]

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=%s
            AND password=%s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        if user:

            # ======================
            # SAVE SESSION
            # ======================

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]

            session["user_role"] = user["role"]

            # ======================
            # ROLE CHECK
            # ======================

            if user["role"] == "Admin":

                return redirect("/admin")

            else:

                return redirect("/dashboard")

        else:

            return "Invalid Email or Password"

    except Exception as e:

        return f"Login Error: {str(e)}"

# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ==============================
# ADMIN DASHBOARD
# ==============================

@app.route("/admin")
def admin_dashboard():

    cursor.execute("""
    SELECT *
    FROM complaints
    ORDER BY id DESC
    """)

    complaints = cursor.fetchall()

    cursor.execute("""
    SELECT COUNT(*) AS total
    FROM complaints
    """)

    total = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) AS pending
    FROM complaints
    WHERE status='Pending'
    """)

    pending = cursor.fetchone()["pending"]

    cursor.execute("""
    SELECT COUNT(*) AS resolved
    FROM complaints
    WHERE status='Resolved'
    """)

    resolved = cursor.fetchone()["resolved"]

    cursor.execute("""
    SELECT COUNT(*) AS high
    FROM complaints
    WHERE severity='High'
    """)

    high = cursor.fetchone()["high"]

    cursor.execute("""
    SELECT issue_type,
    COUNT(*) AS total

    FROM complaints

    GROUP BY issue_type
    """)

    issue_data = cursor.fetchall()

    cursor.execute("""
    SELECT severity,
    COUNT(*) AS total

    FROM complaints

    GROUP BY severity
    """)

    severity_data = cursor.fetchall()

    cursor.execute("""
    SELECT MONTH(created_at) AS month,
    COUNT(*) AS total

    FROM complaints

    GROUP BY MONTH(created_at)
    """)

    monthly_data = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM complaints
    ORDER BY id DESC
    LIMIT 5
    """)

    activities = cursor.fetchall()

    return render_template(

        "admin.html",

        complaints=complaints,

        total=total,

        pending=pending,

        resolved=resolved,

        high=high,

        issue_data=issue_data,

        severity_data=severity_data,

        monthly_data=monthly_data,

        activities=activities

    )

# ==============================
# DELETE COMPLAINT
# ==============================

@app.route("/delete/<int:id>")
def delete_complaint(id):

    try:

        cursor.execute(
            "SELECT image FROM complaints WHERE id=%s",
            (id,)
        )

        complaint = cursor.fetchone()

        if complaint:

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                complaint["image"]
            )

            if os.path.exists(image_path):

                os.remove(image_path)

        cursor.execute(
            "DELETE FROM complaints WHERE id=%s",
            (id,)
        )

        db.commit()

        return redirect("/admin")

    except Exception as e:

        return f"Delete Error: {str(e)}"

# ==============================
# CHANGE STATUS
# ==============================

@app.route("/status/<int:id>/<status>")
def change_status(id, status):

    try:

        cursor.execute(
            """
            UPDATE complaints
            SET status=%s
            WHERE id=%s
            """,
            (status, id)
        )

        db.commit()

        return redirect("/admin")

    except Exception as e:

        return f"Status Error: {str(e)}"

# ==============================
# DISPLAY UPLOADED IMAGE
# ==============================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# ==============================
# IMAGE UPLOAD + AI DETECTION
# ==============================

@app.route("/upload", methods=["POST"])
def upload():

    try:

        if "user_email" not in session:

            return redirect("/")

        image = request.files["image"]

        latitude = request.form.get("latitude")

        longitude = request.form.get("longitude")

        # Save Image
        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            image.filename
        )

        image.save(image_path)

        # Open Image
        img = Image.open(image_path)

        # Gemini Prompt
        prompt = """
        You are an AI civic issue detector.

        Analyze the uploaded image carefully.

        Return ONLY JSON format:

        {
          "issue_type": "",
          "severity": "",
          "description_english": "",
          "description_marathi": "",
          "solution": ""
        }

        Possible issue types:
        - pothole
        - garbage
        - water leakage
        - broken streetlight
        - road crack
        - drainage issue

        Generate complaint in:
        1. English
        2. Marathi
        """

        # Gemini Response
        response = model.generate_content([prompt, img])

        result = response.text.strip()

        # Clean JSON
        result = result.replace("```json", "")
        result = result.replace("```", "")

        data = json.loads(result)

        # ======================
        # CHECK DUPLICATE IMAGE
        # ======================

        check_query = """
        SELECT * FROM complaints
        WHERE image = %s
        """

        cursor.execute(check_query, (image.filename,))

        existing_image = cursor.fetchone()

        if not existing_image:

            sql = """
            INSERT INTO complaints
            (
                image,
                issue_type,
                severity,
                description,
                description_marathi,
                solution,
                latitude,
                longitude,
                status,
                user_email
            )

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                image.filename,
                data["issue_type"],
                data["severity"],
                data["description_english"],
                data["description_marathi"],
                data["solution"],
                latitude,
                longitude,
                "Pending",
                session["user_email"]
            )

            cursor.execute(sql, values)

            db.commit()

        else:

            print("Image already exists")

        return redirect("/dashboard")

    except Exception as e:

        return f"Error: {str(e)}"

# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    if "user_email" not in session:

        return redirect("/")

    # =========================
    # USER COMPLAINTS ONLY
    # =========================

    cursor.execute(
        """
        SELECT *
        FROM complaints
        WHERE user_email=%s
        ORDER BY id DESC
        """,
        (session["user_email"],)
    )

    complaints = cursor.fetchall()
    
    
    

    # =========================
    # TOTAL COMPLAINTS
    # =========================

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE user_email=%s
        """,
        (session["user_email"],)
    )

    total_complaints = cursor.fetchone()["total"]

    # =========================
    # PENDING
    # =========================

    cursor.execute(
        """
        SELECT COUNT(*) AS pending
        FROM complaints
        WHERE status='Pending'
        AND user_email=%s
        """,
        (session["user_email"],)
    )

    pending = cursor.fetchone()["pending"]

    # =========================
    # RESOLVED
    # =========================

    cursor.execute(
        """
        SELECT COUNT(*) AS resolved
        FROM complaints
        WHERE status='Resolved'
        AND user_email=%s
        """,
        (session["user_email"],)
    )

    resolved = cursor.fetchone()["resolved"]

    # =========================
    # HIGH SEVERITY
    # =========================

    cursor.execute(
        """
        SELECT COUNT(*) AS high
        FROM complaints
        WHERE severity='High'
        AND user_email=%s
        """,
        (session["user_email"],)
    )

    high = cursor.fetchone()["high"]

    # =========================
    # ISSUE CHART DATA
    # =========================

    cursor.execute(
        """
        SELECT issue_type,
        COUNT(*) AS total

        FROM complaints

        WHERE user_email=%s

        GROUP BY issue_type
        """,
        (session["user_email"],)
    )

    issue_data = cursor.fetchall()

    # =========================
    # SEVERITY CHART DATA
    # =========================

    cursor.execute(
        """
        SELECT severity,
        COUNT(*) AS total

        FROM complaints

        WHERE user_email=%s

        GROUP BY severity
        """,
        (session["user_email"],)
    )

    severity_data = cursor.fetchall()

    # =========================
    # LATEST AI RESULT
    # =========================

    latest_result = None

    if complaints:

        latest_result = complaints[0]

    return render_template(

        "dashboard.html",

        complaints=complaints,

        total_complaints=total_complaints,

        pending=pending,

        resolved=resolved,

        high=high,

        issue_data=issue_data,

        severity_data=severity_data,

        latest_result=latest_result,

        user_name=session["user_name"]

    )
    
@app.route("/complaint/<int:id>")
def complaint_details(id):

    cursor.execute(
        """
        SELECT * FROM complaints
        WHERE id=%s
        """,
        (id,)
    )

    complaint = cursor.fetchone()

    return render_template(
        "complaint_details.html",
        complaint=complaint
    )
    
    
    

# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
    
    
    