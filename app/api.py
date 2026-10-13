from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import sqlite3
import base64
import os
import glob
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = 'data/attendance.db'
DATASET_PATH = 'data/dataset'

# Ensure directories exist
os.makedirs(DATASET_PATH, exist_ok=True)
os.makedirs('data', exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            roll_number TEXT,
            name TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    prn = data.get('prn')
    image_data = data.get('image')

    if not all([name, prn, image_data]):
        return jsonify({"status": "error", "message": "Missing data"}), 400

    # Check if user already exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE roll_number = ?", (prn,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Student already registered."}), 400
    conn.close()

    # Save the base64 image as a reference photo
    try:
        encoded_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(encoded_data)
        img_path = os.path.join(DATASET_PATH, f"{prn}.jpg")
        
        with open(img_path, "wb") as f:
            f.write(img_bytes)

        # Force DeepFace to update cache by running a dummy check
        if os.path.exists(os.path.join(DATASET_PATH, "representations_vgg_face.pkl")):
            os.remove(os.path.join(DATASET_PATH, "representations_vgg_face.pkl"))

        return jsonify({"status": "success", "message": f"Successfully registered {name}."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        return jsonify({"status": "error", "message": "No image provided"}), 400

    try:
        # Save temporary image for DeepFace
        encoded_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(encoded_data)
        temp_path = "temp_scan.jpg"
        
        with open(temp_path, "wb") as f:
            f.write(img_bytes)

        # Run DeepFace search
        dfs = DeepFace.find(img_path=temp_path, db_path=DATASET_PATH, enforce_detection=False, silent=True)
        os.remove(temp_path)

        if len(dfs) > 0 and not dfs[0].empty:
            matched_path = dfs[0].iloc[0]['identity']
            # Extract PRN from filename (e.g. data/dataset/24070123103.jpg -> 24070123103)
            prn = os.path.splitext(os.path.basename(matched_path))[0]
            if not prn.strip() or prn.strip().lower() in {"none", "null", "undefined"}:
                return jsonify({"status": "error", "message": "Matched image filename does not contain a valid PRN."}), 500

            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            # Save attendance to SQLite
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attendance (date, time, roll_number, name, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, time_str, prn, f"Student {prn}", "Present"))
            conn.commit()
            conn.close()

            return jsonify({
                "status": "success",
                "prn": prn,
                "roll_number": prn,
                "name": f"Student {prn}"
            }), 200
        else:
            return jsonify({"status": "error", "message": "Face not recognized."}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/records', methods=['GET'])
def get_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, roll_number, name, status FROM attendance ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for row in rows:
        records.append({
            "date": row[0],
            "time": row[1],
            "roll_number": row[2],
            "name": row[3],
            "status": row[4]
        })
    return jsonify(records), 200


@app.route('/delete/<prn>', methods=['DELETE'])
def delete_record(prn):
    try:
        # 1. Delete from Database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE roll_number = ?", (prn,))
        conn.commit()
        conn.close()

        # 2. Delete the student's reference image
        img_path = os.path.join(DATASET_PATH, f"{prn}.jpg")
        if os.path.exists(img_path):
            os.remove(img_path)

        # 3. Wipe DeepFace cache files so the AI fully forgets the user
        cache_files = glob.glob(os.path.join(DATASET_PATH, "representations_*.pkl"))
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
            except OSError:
                pass

        return jsonify({"status": "success", "message": f"Data for {prn} permanently deleted."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)