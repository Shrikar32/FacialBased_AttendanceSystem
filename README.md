# Facial Recognition Attendance System
College MVP built with Python and OpenCV.
# Facial Recognition Attendance System

**Team Members:**
* Shrikar Mujumdar (PRN: 24070123103)
* Soham Garge (PRN: 24070123110)
* Piyush Pawar (PRN: 24070123145)

**Program:** B.Tech Electronics & Telecommunication Engineering (Embedded Systems)  
**Institution:** Symbiosis Institute of Technology, Pune  

## Project Overview
This project is an automated, lightweight Facial Recognition Attendance System designed to replace manual roll calls. Built with Python, OpenCV, and DeepFace, the system captures student biometric data, generates facial embeddings, and performs real-time asynchronous recognition via a webcam feed.

## Features
*   **Real-Time Recognition:** Asynchronous multi-threading ensures the webcam runs smoothly at 30 FPS while AI inference runs in the background.
*   **Local Database:** Uses SQLite to store student data and attendance logs securely without external dependencies.
*   **Duplicate Prevention:** Database-level constraints automatically prevent marking attendance multiple times for the same student on the same day.
*   **CSV Export:** One-click export of attendance records for administrative use.
*   **Graphical Interface:** Clean and simple Tkinter GUI for seamless operation.

## Technology Stack
*   **Language:** Python 3.10+
*   **Computer Vision:** OpenCV (`cv2`)
*   **Facial Recognition:** DeepFace (RetinaFace Detector Backend)
*   **Database:** SQLite3
*   **GUI:** Tkinter
*   **Data Handling:** Pandas

## Requirements
*   Webcam (720p/1080p recommended)
*   Python 3.10 or higher
*   Requirements listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```powershell
   git clone https://github.com/YOUR_USERNAME/face-attendance-system.git
   cd face-attendance-system
   ```

2. Set up the environment and launch the desktop GUI:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python run.py
   ```

## Web Frontend API

The desktop GUI (`run.py`) and the web frontend API are separate processes. To use the web scanner, attendance logs, and delete action, start the API from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app\database.py
.\.venv\Scripts\python.exe app\api.py
```

The API listens on `http://127.0.0.1:5000` and provides `POST /register`, `POST /recognize`, `GET /records`, and `DELETE /delete/<prn>`. Keep it running while using the frontend. Restart it after changing the API code.

## System Workflow
1. Registration
Click [ REGISTER STUDENT ]. The system prompts for a PRN and Name. A webcam window opens with a bounding box guide. Pressing c captures the frame, saves the image to data/faces/, and logs the student details in the SQLite database.

2. Attendance
Click [ START ATTENDANCE ]. The system captures live video frames and dispatches them to a background thread. DeepFace calculates embeddings using the RetinaFace backend and verifies cosine similarity against the local face database. If a match is found, attendance is marked.

3. Export
Click [ EXPORT CSV ]. The system joins the relational tables, generates a formatted view, and exports attendance_export.csv to the data/ directory.

Project Architecture
Plaintext
face-attendance-system/
│
├── app/
│   ├── main.py          # Main Tkinter GUI application
│   ├── database.py      # SQLite initialization and schema
│   ├── register.py      # User registration and face capture
│   └── recognize.py     # Multi-threaded recognition engine
│
├── data/
│   ├── attendance.db    # Relational database
│   └── faces/           # Stored reference images and embedding caches
│
├── run.py               # Entry point script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
Database Schema
students: id (PK), roll_number (UNIQUE), name, image_path, created_at

attendance: id (PK), student_id (FK), date, time, status, UNIQUE(student_id, date)

Limitations
Accuracy is dependent on ambient classroom lighting.

The SQLite database is stored locally and requires network migration for campus-wide deployment.

Vulnerable to basic 2D photo spoofing (no depth-mapping or liveness detection implemented).

Future Scope
Anti-Spoofing: Integration of blink detection or depth-mapping to prevent photo spoofing.

Cloud Database: Migrating from SQLite to PostgreSQL/Firebase for centralized synchronization.

Batch Processing: Upgrading the pipeline to recognize multiple faces simultaneously in a crowded frame.