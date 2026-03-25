# AI-Based Interview Question Generator

## 🚀 Overview
This project is a web-based application that generates personalized interview questions based on:
- Job Description
- User Resume
- Optional Company Description

It uses Natural Language Processing (NLP) and rule-based logic to analyze inputs and produce relevant technical, HR, behavioral, and managerial questions.

---

## 🎯 Features
- Upload or paste Resume, Job Description, and Company Description
- Supports file formats: `.txt`, `.docx`, `.pdf`
- Generates:
  - Technical Questions
  - HR Questions
  - Behavioral Questions
  - Managerial Questions
- Smart keyword matching between resume and job requirements
- Identifies skill gaps and strengths
- Adjustable number of generated questions

---

## 🧠 Technologies Used
- Python
- Flask (Web Framework)
- NLP (Keyword Extraction & Text Processing)
- HTML, CSS (Frontend)
- JavaScript (UI interactions)

---

## ⚙️ How It Works
1. Extracts text from uploaded files or user input
2. Identifies important keywords and skills
3. Matches resume with job description
4. Detects common and missing skills
5. Generates personalized interview questions

---

## 📂 Project Structure
```
interview-ai/
│
├── app.py
├── utils.py
├── templates/
│ └── index.html
├── static/
│ └── style.css
└── requirements.txt
```
---

## ▶️ How to Run

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:
```
http://127.0.0.1:5000
```

## 💡 Future Improvements
- Use ML models for better semantic understanding
- Add downloadable report (PDF)
- Improve UI with advanced frontend frameworks
- Add real-time feedback and scoring system

---

## 📌 Conclusion

This project demonstrates how AI-inspired logic and NLP techniques can be used to build a practical tool for interview preparation.

---

## 👩‍💻 Author

Aditi Jain
