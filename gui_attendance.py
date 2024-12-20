#python gui_attendance.py

import tkinter as tk
from tkinter import messagebox
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import json
import subprocess

# Database connection
db = mysql.connector.connect(
    host="localhost",       # Enter your own host here
    user="root",            # Enter your own user here
    password="password",    # Enter your own password here 
    database="AttendanceSystem"
)
cursor = db.cursor()

# Function to log attendance in the database
def log_attendance(student_id):
    sql = "INSERT INTO Attendance (StudentID, Timestamp) VALUES (%s, NOW())"
    cursor.execute(sql, (student_id,))
    db.commit()
    print(f"Attendance logged for StudentID: {student_id}")

# Function to take attendance using facial recognition
def take_attendance():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trainer.yml")
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        cap = cv2.VideoCapture(0)

        attendance_logged = False  # Flag to indicate if attendance has been logged

        while not attendance_logged:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

            for (x, y, w, h) in faces:
                id_, conf = recognizer.predict(gray[y:y+h, x:x+w])
                if conf >= 60:
                    with open("names.json", "r") as f:
                        names = json.load(f)
                    name = names.get(str(id_), "Unknown")
                    print(f"Detected: {name}")
                    log_attendance(id_)
                    attendance_logged = True  # Stop further attendance logging
                    break  # Exit the loop once attendance is logged
                else:
                    print("Face not recognized.")

            cv2.imshow("Frame", frame)
            if cv2.waitKey(20) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        if attendance_logged:
            messagebox.showinfo("Attendance", "Attendance logged successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to add a student to the database
def add_student():
    def submit():
        first_name = entry_first_name.get()
        last_name = entry_last_name.get()
        major = entry_major.get()
        email = entry_email.get()

        sql = "INSERT INTO Student (FirstName, LastName, Major, Email, ClassID) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (first_name, last_name, major, email, None))
        # TO DO Perhaps We run the face taker here, we have to add photo to the student table
        db.commit()

        messagebox.showinfo("Success", f"Student {first_name} {last_name} added!")
        subprocess.run(['python3', 'face_taker.py', first_name])  # Run scripts
        subprocess.run(['python3', 'face_train.py']) 
        add_student_window.destroy()

    add_student_window = tk.Toplevel()
    add_student_window.title("Add Student")

    tk.Label(add_student_window, text="First Name").grid(row=0, column=0)
    tk.Label(add_student_window, text="Last Name").grid(row=1, column=0)
    tk.Label(add_student_window, text="Major").grid(row=2, column=0)
    tk.Label(add_student_window, text="Email").grid(row=3, column=0)

    entry_first_name = tk.Entry(add_student_window)
    entry_last_name = tk.Entry(add_student_window)
    entry_major = tk.Entry(add_student_window)
    entry_email = tk.Entry(add_student_window)

    entry_first_name.grid(row=0, column=1)
    entry_last_name.grid(row=1, column=1)
    entry_major.grid(row=2, column=1)
    entry_email.grid(row=3, column=1)

    tk.Button(add_student_window, text="Scan Face Now", command=submit).grid(row=4, column=0, columnspan=2)



from tkinter import ttk

# Function to generate and display attendance reports
def generate_attendance_report():
    # Query to fetch all students and their attendance status
    query = """
    SELECT 
        s.StudentID, 
        CONCAT(s.FirstName, ' ', s.LastName) AS Name, 
        a.AttendanceID, 
        a.Timestamp, 
        CASE 
            WHEN a.AttendanceID IS NOT NULL THEN 'Present' 
            ELSE 'Absent' 
        END AS Status
    FROM Student s
    LEFT JOIN Attendance a ON s.StudentID = a.StudentID
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Create a new window for the attendance report
    report_window = tk.Toplevel()
    report_window.title("Attendance Logs")

    # Add a Treeview widget
    tree = ttk.Treeview(
        report_window, 
        columns=("StudentID", "Name", "AttendanceID", "Timestamp", "Status"), 
        show="headings"
    )
    tree.heading("StudentID", text="StudentID")
    tree.heading("Name", text="Name")
    tree.heading("AttendanceID", text="AttendanceID")
    tree.heading("Timestamp", text="Timestamp")
    tree.heading("Status", text="Status")

    # Insert the data into the Treeview
    for row in rows:
        tree.insert("", tk.END, values=row)

    tree.pack(fill=tk.BOTH, expand=True)

    # Add a scroll bar
    scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Inform the user
    messagebox.showinfo("Attendance Report", "Logs displayed in a new window.")

# Main GUI window
root = tk.Tk()
root.title("Facial Recognition Attendance System")

tk.Label(root, text="Facial Recognition Attendance System", font=("Arial", 16)).pack(pady=20)

tk.Button(root, text="Take Attendance", command=take_attendance, width=20).pack(pady=10)
tk.Button(root, text="Add Student", command=add_student, width=20).pack(pady=10)
tk.Button(root, text="View Attendance Report", command=generate_attendance_report, width=20).pack(pady=10)

root.mainloop()
