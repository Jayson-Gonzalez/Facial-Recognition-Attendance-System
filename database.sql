-- Create database
CREATE DATABASE AttendanceSystem;

-- Use the database
USE AttendanceSystem;


-- Room table
CREATE TABLE Room (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    RoomName VARCHAR(50),
    Building VARCHAR(50),
    Capacity INT
);

-- Professor table
CREATE TABLE Professor (
    ProfessorID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100),
    Department VARCHAR(50),
    RoomID INT,
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

-- Class table WE HAVE TO ADD PHOTOS AS A VARIABLE 
CREATE TABLE Class (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(100),
    ClassCode VARCHAR(50),
    ProfessorID INT,
    RoomID INT,
    FOREIGN KEY (ProfessorID) REFERENCES Professor(ProfessorID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

-- Student table
CREATE TABLE Student (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Major VARCHAR(50),
    Email VARCHAR(100),
    ClassID INT,
    FOREIGN KEY (ClassID) REFERENCES Class(ClassID)
);

-- Attendance table
CREATE TABLE Attendance (
    AttendanceID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    Timestamp DATETIME,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);
