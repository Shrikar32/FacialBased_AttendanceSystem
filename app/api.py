from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import sqlite3
from deepface import DeepFace
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)
CORS(app) 

# Ensure the dataset folder exists when the app starts
os.makedirs("data/dataset", exist_ok=True)

def save_base64_image(base64_string, file_path):
    """Safely decodes a base64 string from the browser and saves it as a JPG"""
    if "," in base64_string:
        base64_string = base64_string.split(',')[1]
    
    with open(file_path, "wb") as fh:
        fh.write(base64.b64decode(base64_string))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    roll_number = data.get('roll_number') or data.get('prn')
    name = data.get('name')
    image_data = data.get('image')
    
    if roll_number is None or not str(roll_number).strip() or not name or not image_data:
        return jsonify({"status": "error", "message": "Missing data"}), 400
    roll_number = str(roll_number).strip()
    if roll_number.lower() in {"none", "null"}:
        return jsonify({"status": "error", "message": "A valid PRN is required"}), 400
        
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (roll_number TEXT PRIMARY KEY, name TEXT, image_path TEXT)''')
    
    # Check if exists
    cursor.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Student already registered."}), 400
        
    # Save Image Directly to Disk
    img_path = f"data/dataset/{roll_number}.jpg"
    try:
        save_base64_image(image_data, img_path)
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": f"Failed to save image file: {str(e)}"}), 500
    
    # Save to DB
    cursor.execute("INSERT INTO students (roll_number, name, image_path) VALUES (?, ?, ?)", 
                   (roll_number, name, img_path))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": f"{name} registered successfully!"})

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json
    image_data = data.get('image')
    
    temp_path = "data/temp_web.jpg"
    save_base64_image(image_data, temp_path)
    
    try:
        dfs = DeepFace.find(img_path=temp_path, db_path="data/dataset", detector_backend="retinaface", enforce_detection=False, silent=True)
        if len(dfs) > 0 and not dfs[0].empty:
            matched_file = dfs[0].iloc[0]['identity'].replace("\\", "/")
            roll_number = matched_file.split("/")[-1].split(".")[0]
            
            # Log Attendance
            conn = sqlite3.connect("data/attendance.db")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (roll_number TEXT, name TEXT, date TEXT, time TEXT, status TEXT)''')
            
            cursor.execute("SELECT roll_number, name FROM students WHERE roll_number=?", (roll_number,))
            student = cursor.fetchone()
            
            if student:
                st_roll, st_name = student
                if not st_roll or str(st_roll).strip().lower() in {"none", "null"}:
                    conn.close()
                    return jsonify({
                        "status": "error",
                        "message": "This student has no valid PRN. Re-register the student with a PRN.",
                    }), 400
                today = datetime.now().strftime("%Y-%m-%d")
                time_now = datetime.now().strftime("%H:%M:%S")
                
                cursor.execute("INSERT INTO attendance (roll_number, name, date, time, status) VALUES (?, ?, ?, ?, ?)",
                               (st_roll, st_name, today, time_now, "Present"))
                conn.commit()
                conn.close()
                
                # CORRECTED RESPONSE HERE
                return jsonify({
                    "status": "success", 
                    "message": f"Attendance marked for {st_name}",
                    "name": st_name,
                    "roll_number": st_roll,
                    "prn": st_roll,
                    "id": st_roll,
                    "student_id": st_roll
                })
    except Exception as e:
        app.logger.error(f"DeepFace Recognition Error: {e}")
        pass
        
    return jsonify({"status": "error", "message": "Unknown Face"})

@app.route('/records', methods=['GET'])
def get_records():
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (roll_number TEXT, name TEXT, date TEXT, time TEXT, status TEXT)''')
    cursor.execute("""
        SELECT a.date, a.time, s.roll_number, s.name, a.status 
        FROM attendance a JOIN students s ON a.roll_number = s.roll_number
        ORDER BY a.date DESC, a.time DESC
    """)
    records = [{"date": r[0], "time": r[1], "roll_number": r[2], "name": r[3], "status": r[4]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(records)

@app.route('/delete/<prn>', methods=['DELETE', 'OPTIONS'])
def delete_student(prn):
    if request.method == 'OPTIONS':
        return '', 204

    prn = prn.strip()
    if not prn or prn in {'.', '..'} or '\x00' in prn or '/' in prn or '\\' in prn:
        return jsonify({"status": "error", "message": "A valid PRN is required."}), 400

    conn = sqlite3.connect("data/attendance.db")
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT roll_number, image_path FROM students WHERE roll_number = ?", (prn,))
        student = cursor.fetchone()
        
        if student is None:
            return jsonify({"status": "error", "message": f"No student found for PRN {prn}."}), 404

        student_roll, stored_image_path = student
        image_path = Path(stored_image_path).resolve()
        dataset_path = Path("data/dataset").resolve()
        
        if image_path.parent != dataset_path:
            return jsonify({"status": "error", "message": "Student image path is invalid."}), 500

        with conn:
            cursor.execute("DELETE FROM attendance WHERE roll_number = ?", (student_roll,))
            cursor.execute("DELETE FROM students WHERE roll_number = ?", (student_roll,))
    except sqlite3.Error as e:
        app.logger.exception("Failed to delete student with PRN %s", prn)
        return jsonify({"status": "error", "message": "The student could not be deleted."}), 500
    finally:
        conn.close()

    try:
        if image_path.is_file():
            image_path.unlink()
        for cache_path in dataset_path.glob("representations_*.pkl"):
            if cache_path.is_file():
                cache_path.unlink()
    except OSError:
        return jsonify({
            "status": "error",
            "message": "The student was removed from the database, but their image or face cache could not be removed.",
        }), 500

    # CORRECTED DELETE RESPONSE BACK TO NORMAL
    return jsonify({"status": "success", "message": f"Deleted student {prn}."})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
