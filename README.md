# CV Analyzer - Flask Web Application
Intelligent CV Analyzer using String Matching Algorithms (Brute Force, Rabin-Karp, KMP) for Automated Skill Extraction and Job Fit Evaluation.
## Features
- **Three String Matching Algorithms:**
  - Brute Force Algorithm
  - Rabin-Karp Algorithm  
  - Knuth-Morris-Pratt (KMP) Algorithm

- **CV Analysis:**
  - Upload PDF, DOCX, or TXT files
  - Automatic keyword extraction from job descriptions
  - Skill matching and relevance scoring
  - Case-sensitive/insensitive matching

- **Performance Analysis:**
  - Execution time comparison
  - Character comparison counts
  - Performance charts and tables
  - Algorithm recommendations
## Setup Instructions
### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using the specific Python interpreter:
```bash
"C:\Users\Muhammad Noor\AppData\Local\Programs\Python\Python313\python.exe" -m pip install -r requirements.txt
```
### 2. Run the Application

```bash
python app.py
```

### 3. Access the Application
Open your browser and go to:
```
http://localhost:5000
```

## Project Structure
```
asst/
├── app.py                  # Flask application with string matching algorithms
├── requirements.txt         # Dependencies
├── templates/              # HTML templates
│   ├── index.html         # CV Analysis page
│   └── results.html       # Performance Comparison page
└── static/                # Static files (CSS,JS)
    └── styles.css          # Styling
```
## Usage
1. **Analyze a CV:**
   - Go to the home page (http://localhost:5000)
   - Upload a CV file (PDF, DOCX, or TXT)
   - Optionally paste a job description or provide keywords
   - Click "Analyze CV"
   - View results for all three algorithms

2. **Performance Comparison:**
   - After analyzing a CV, click "View Performance Comparison"
   - See detailed performance metrics
   - View charts and algorithm recommendations

## Technologies Used
- **Backend:** Flask 3.0.0
- **Frontend:** HTML5, CSS3, JavaScript
- **Libraries:** PyPDF2, python-docx
- **Charts:** Chart.js

## Algorithms Implemented
### 1. Brute Force
- **Time Complexity:** O(n*m)
- **Space Complexity:** O(1)
- Simple but less efficient for large texts

### 2. Rabin-Karp
- **Time Complexity:** O(n+m) average, O(n*m) worst case
- **Space Complexity:** O(1)
- Good average-case performance with hash-based matching

### 3. Knuth-Morris-Pratt (KMP)
- **Time Complexity:** O(n+m)
- **Space Complexity:** O(m)
- Guaranteed linear time with optimal performance

## Troubleshooting
### ModuleNotFoundError
If you get import errors, ensure you're using the correct Python interpreter:

```bash
# Checking Python version
python --version

# Installing packages for that Python
python -m pip install -r requirements.txt
```

Or use Python 3.13 directly:
```bash
"C:\Users\Muhammad Noor\AppData\Local\Programs\Python\Python313\python.exe" -m pip install -r requirements.txt
"C:\Users\Muhammad Noor\AppData\Local\Programs\Python\Python313\python.exe" app.py
```

