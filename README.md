# Smart Civic AI – AI-Powered Civic Issue Reporting System

Smart Civic AI is an AI-powered civic issue reporting application that allows users to upload images of civic problems and automatically analyze them using the **Gemini API**. The system identifies the type and severity of the issue and generates descriptions and solutions in both **English and Marathi**.

## 🚀 Key Features

* **AI Image Analysis** – Analyzes uploaded civic issue images using Gemini.
* **Civic Issue Detection** – Identifies issues such as potholes, garbage, water leakage, broken streetlights, road cracks, and drainage problems.
* **Severity Detection** – Determines the severity of detected civic issues.
* **AI-Generated Description** – Generates a clear description of the detected issue.
* **Bilingual AI Output** – Generates issue descriptions in both English and Marathi.
* **AI-Generated Solution** – Provides a suggested solution for the detected civic issue.
* **Location Tracking** – Stores latitude and longitude of reported issues.
* **Complaint Management** – Users can track their submitted complaints and their status.
* **Admin Dashboard** – Admins can view complaints, severity statistics, issue types, monthly activity, and update complaint status.
* **User Authentication** – Supports user registration, login, sessions, and role-based access.

## 🤖 Generative AI

The project uses the **Gemini API** for multimodal image analysis.

When a user uploads an image, Gemini analyzes the image and returns structured information including:

```text
Issue Type
Severity
English Description
Marathi Description
Suggested Solution
```

For example:

**Uploaded Image:** Pothole on a road

**AI Analysis:**

* Issue Type: Pothole
* Severity: High
* Description: Road surface contains a large pothole that may create a safety risk.
* Marathi Description: रस्त्यावर मोठा खड्डा असून तो नागरिकांच्या सुरक्षिततेसाठी धोका निर्माण करू शकतो.
* Solution: Repair and resurface the damaged section of the road.

## 🔄 How It Works

```text
User
 ↓
Upload Civic Issue Image
 ↓
Gemini Vision Analysis
 ↓
Issue Detection
 ↓
Severity Analysis
 ↓
English + Marathi Description
 ↓
Suggested Solution
 ↓
MySQL Database
 ↓
User Dashboard / Admin Dashboard
```

## 🛠️ Tech Stack

* **Python**
* **Flask**
* **Google Gemini API**
* **Pillow**
* **MySQL**
* **HTML / CSS**
* **Jinja Templates**

## 🧠 AI Capabilities

The AI can analyze images for common civic issues including:

* Potholes
* Garbage
* Water leakage
* Broken streetlights
* Road cracks
* Drainage issues

The application uses Gemini's multimodal capabilities to understand the uploaded image and generate structured civic issue information.

## 📊 Admin Dashboard

The admin dashboard provides:

* Total complaints
* Pending complaints
* Resolved complaints
* High-severity complaints
* Issue-type statistics
* Severity statistics
* Monthly complaint activity
* Recent complaint activities
* Complaint status management

## 🎯 Purpose

Smart Civic AI aims to simplify civic issue reporting by combining **Generative AI, image analysis, location data, and complaint management** into a single platform.

Instead of manually describing a civic problem, users can upload an image and let AI generate the relevant issue details and suggested solution.

## 📌 Project Highlights

* Built an AI-powered image-based civic issue reporting system.
* Integrated **Google Gemini API** for multimodal image analysis.
* Implemented automated issue type and severity detection.
* Generated bilingual English and Marathi descriptions.
* Generated AI-based solutions for reported civic issues.
* Implemented Flask backend and MySQL database integration.
* Built separate user and admin dashboards.
