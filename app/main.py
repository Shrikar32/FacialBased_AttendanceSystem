import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import pandas as pd
import os
import sys
import shutil
import subprocess

# Set modern dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def run_register():
    # Use subprocess to prevent the black CMD window from popping up
    subprocess.Popen([sys.executable, "app/register.py"])

def run_attendance():
    # Use subprocess to launch silently in the background
    subprocess.Popen([sys.executable, "app/recognize.py"])

def view_attendance():
    conn = sqlite3.connect("data/attendance.db")
    df = pd.read_sql_query("""
        SELECT a.date, a.time, s.roll_number, s.name, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id
    """, conn)
    conn.close()
    
    top = ctk.CTkToplevel()
    top.title("Attendance Records")
    top.geometry("600x400")
    
    text = ctk.CTkTextbox(top, width=580, height=380, font=("Courier", 14))
    text.pack(padx=10, pady=10)
    
    if df.empty:
        text.insert("0.0", "No attendance records found.")
    else:
        text.insert("0.0", df.to_string(index=False))
    text.configure(state="disabled")

def export_csv():
    conn = sqlite3.connect("data/attendance.db")
    df = pd.read_sql_query("""
        SELECT a.date, a.time, s.roll_number, s.name, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id
    """, conn)
    conn.close()
    
    if df.empty:
        messagebox.showinfo("Export", "No attendance records found.")
        return
        
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/attendance_export.csv", index=False)
    messagebox.showinfo("Export", "Successfully exported to data/attendance_export.csv!")

def delete_all_data():
    confirm = messagebox.askyesno("WARNING", "Delete ALL students and attendance? This cannot be undone.")
    if confirm:
        try:
            # Clear Database
            conn = sqlite3.connect("data/attendance.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students")
            cursor.execute("DELETE FROM attendance")
            conn.commit()
            conn.close()
            
            # Delete Face Images and AI Cache
            if os.path.exists("data/faces"):
                shutil.rmtree("data/faces")
                os.makedirs("data/faces")
                
            messagebox.showinfo("Success", "All records and faces deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete: {e}")

def create_gui():
    root = ctk.CTk()
    root.title("Facial Attendance System")
    root.geometry("500x520")
    
    title_label = ctk.CTkLabel(root, text="FACIAL ATTENDANCE", font=("Courier", 26, "bold"))
    title_label.pack(pady=(30, 20))
    
    btn_reg = ctk.CTkButton(root, text="Register New Student", height=45, font=("Arial", 15), command=run_register)
    btn_reg.pack(fill="x", padx=60, pady=10)
    
    btn_att = ctk.CTkButton(root, text="Start Attendance System", height=45, font=("Arial", 15), fg_color="#28a745", hover_color="#218838", command=run_attendance)
    btn_att.pack(fill="x", padx=60, pady=10)
    
    btn_view = ctk.CTkButton(root, text="View Attendance", height=45, font=("Arial", 15), command=view_attendance)
    btn_view.pack(fill="x", padx=60, pady=10)
    
    btn_exp = ctk.CTkButton(root, text="Export to CSV", height=45, font=("Arial", 15), command=export_csv)
    btn_exp.pack(fill="x", padx=60, pady=10)
    
    btn_del = ctk.CTkButton(root, text="Delete All Data", height=45, font=("Arial", 15), fg_color="#dc3545", hover_color="#c82333", command=delete_all_data)
    btn_del.pack(fill="x", padx=60, pady=(30, 10))
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()