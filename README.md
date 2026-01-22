# AWARE AI Content Detection

Web-based implementation of the AWARE (AI Writing Analysis & Risk Evaluation) framework.

## Setup
1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Run
```bash
uvicorn backend.main:app --reload
```

Open `http://localhost:8000`.

## Notes
- Upload `.doc`, `.docx`, `.txt`, `.md`, or `.pdf` files (max 10 MB).
- Optional original file enables contextual Category C checks.
- Track Changes-aware markers (Category J) are only active for `.docx` files with tracked edits.
