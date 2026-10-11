import cv2
import sqlite3
from deepface import DeepFace
from datetime import datetime
import os
import threading

display_msg = "Scanning..."
is_recognizing = False

# This will now work perfectly with OpenCV 4.10
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def mark_attendance(roll_number):
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM students WHERE roll_number=?", (roll_number,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return "Unknown"
        
    student_id, name = student
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    try:
        cursor.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)",
                       (student_id, today, current_time, "Present"))
        conn.commit()
        msg = f"{name} (Marked)"
    except sqlite3.IntegrityError:
        msg = f"{name} (Already Marked)"
        
    conn.close()
    return msg

def recognize_face_background(frame_path):
    global display_msg, is_recognizing
    try:
        dfs = DeepFace.find(img_path=frame_path, db_path="data/faces", detector_backend="retinaface", enforce_detection=False, silent=True)
        
        if len(dfs) > 0 and not dfs[0].empty:
            matched_file = dfs[0].iloc[0]['identity'].replace("\\", "/")
            filename = matched_file.split("/")[-1]
            roll_number = filename.split(".")[0]
            display_msg = mark_attendance(roll_number)
        else:
            display_msg = "Unknown"
    except Exception:
        display_msg = "Scanning..."
    finally:
        is_recognizing = False

def start_recognition():
    global display_msg, is_recognizing
    print("\n--- STARTING ATTENDANCE SYSTEM ---")
    print("Press 'q' to QUIT.")
    
    os.makedirs("data", exist_ok=True)
    temp_path = "data/temp.jpg"
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        for (x, y, w, h) in faces:
            if "Marked" in display_msg:
                color = (0, 255, 0)
            elif "Unknown" in display_msg:
                color = (0, 0, 255)
            else:
                color = (255, 255, 0)
                
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y-35), (x+w, y), color, cv2.FILLED)
            cv2.putText(frame, display_msg, (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.imshow("Attendance Camera", frame)
        
        if not is_recognizing and len(faces) > 0:
            cv2.imwrite(temp_path, frame)
            is_recognizing = True
            threading.Thread(target=recognize_face_background, args=(temp_path,)).start()
                
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_recognition()