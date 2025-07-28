# BloodSense – Biomarker Analyzer & Nutritional Advisor

A Flask web application that analyzes blood test reports and provides personalized health advice using OCR and AI.

## Features

- Upload blood test reports (PDF/PNG/JPG)
- Extract text using OCR (pytesseract)
- Collect user health profile
- Generate personalized health advice using GPT-4
- Create and email PDF reports
- Modern UI with Tailwind CSS

## Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR installed on your system
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`
3. OpenAI API key
4. Email account for sending reports

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bloodsense
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.template .env
   ```
   Then edit `.env` and add your:
   - OpenAI API key
   - Email credentials
   - Flask secret key

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and go to `http://localhost:5000`

3. Upload a blood test report

4. Fill in your health profile

5. Receive the analysis via email

## Project Structure

```
bloodsense/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # For deployment
├── .env.template      # Environment variables template
├── templates/         # HTML templates
│   ├── index.html    # File upload page
│   ├── form.html     # User profile form
│   └── result.html   # Success page
└── utils/            # Helper modules
    ├── ocr.py       # Text extraction
    ├── gpt.py       # OpenAI integration
    └── pdf.py       # PDF generation
```

## Security Notes

- Files are processed in memory and deleted after use
- No health data is stored permanently
- SSL encryption in transit
- API keys and credentials are stored securely in environment variables

Contact-adityasinhasinha06841@gmail.com for queries.
