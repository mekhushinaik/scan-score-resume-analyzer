
# ScanScore — AI Resume Analyzer

ScanScore is a free Streamlit app that analyzes resumes locally and gives ATS-style feedback, job-match scoring, and improvement suggestions without using any API key.

## What it does
- Upload a resume in PDF, DOCX, or TXT format
- Optionally paste a job description
- Get an overall resume score
- See strengths, weaknesses, and actionable improvements
- Compare your resume against a job description

## Why this project
This project was built to help students and job seekers improve their resumes with quick, local, and private analysis.

## Tech Stack
- Python
- Streamlit
- PyPDF / python-docx
- Rule-based text analysis



## How to run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Folder Structure
```bash
project-name/
├── app.py
├── analyzer.py
├── resume_parser.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Future Improvements
- Add better resume formatting checks
- Support more file types
- Improve keyword matching
- Add exportable reports

## License
This project is licensed under the MIT License.
