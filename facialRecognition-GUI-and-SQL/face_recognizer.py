import cv2
import mysql.connector
import json

# Database connection
db = mysql.connector.connect(
    host="localhost",  # Replace with your database host
    user="root",       # Replace with your MySQL username
    password="Rootpass2025",  # Replace with your MySQL password
    database="AttendanceSystem"
)
cursor = db.cursor()

# Function to log attendance in the database
def log_attendance(student_id):
    sql = "INSERT INTO Attendance (StudentID, Timestamp) VALUES (%s, NOW())"
    cursor.execute(sql, (student_id,))
    db.commit()
    print(f"Attendance logged for StudentID: {student_id}")

# Load recognizer and face cascade
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

    for (x, y, w, h) in faces:
        id_, conf = recognizer.predict(gray[y:y+h, x:x+w])
        if conf >= 50:
            with open("names.json", "r") as f:
                names = json.load(f)
            name = names.get(str(id_), "Unknown")
            print(f"Detected: {name}")
            log_attendance(id_)
        else:
            print("Face not recognized.")

    cv2.imshow("Frame", frame)
    if cv2.waitKey(20) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
