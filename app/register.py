import cv2
import os
import sqlite3
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def capture_face(roll_number, name, window):
    # Check if student already exists
    conn = sqlite3.connect("data/attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
    if cursor.fetchone():
        messagebox.showerror("Error", f"Student with PRN {roll_number} is already registered!")
        conn.close()
        return

    os.makedirs("data/faces", exist_ok=True)
    img_path = f"data/faces/{roll_number}.jpg"

    messagebox.showinfo("Camera Ready", "The webcam will now open.\nAlign your face in the box and press 'c' to capture.")
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Camera Error", "Failed to grab frame. Is your webcam connected?")
            break

        # Draw a guide box
        height, width, _ = frame.shape
        start_point = (int(width/2 - 150), int(height/2 - 150))
        end_point = (int(width/2 + 150), int(height/2 + 150))
        cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
        cv2.putText(frame, "Align face & press 'c'", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Face Registration", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            # Save the clean frame without the green guide box
            clean_frame = frame.copy()
            cv2.imwrite(img_path, clean_frame)
            
            cursor.execute("INSERT INTO students (roll_number, name, image_path) VALUES (?, ?, ?)", 
                           (roll_number, name, img_path))
            conn.commit()
            messagebox.showinfo("Success", f"{name} ({roll_number}) registered successfully!")
            break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()
    window.destroy()

def start_registration_gui():
    reg_window = ctk.CTk()
    reg_window.title("Register Student")
    reg_window.geometry("400x350")
    
    ctk.CTkLabel(reg_window, text="STUDENT REGISTRATION", font=("Courier", 20, "bold")).pack(pady=(20, 10))
    
    # Pre-filled placeholder tailored to your format
    prn_entry = ctk.CTkEntry(reg_window, placeholder_text="Enter PRN (e.g. 24070123103)", width=280, height=40)
    prn_entry.pack(pady=15)
    
    name_entry = ctk.CTkEntry(reg_window, placeholder_text="Enter Full Name", width=280, height=40)
    name_entry.pack(pady=15)
    
    def submit():
        roll = prn_entry.get().strip()
        n = name_entry.get().strip()
        if not roll or not n:
            messagebox.showwarning("Input Error", "Please enter both PRN and Name.")
            return
        capture_face(roll, n, reg_window)
        
    submit_btn = ctk.CTkButton(reg_window, text="Open Camera & Capture", width=280, height=45, 
                               fg_color="#28a745", hover_color="#218838", font=("Arial", 14, "bold"), command=submit)
    submit_btn.pack(pady=20)
    
    reg_window.mainloop()

if __name__ == "__main__":
    start_registration_gui()