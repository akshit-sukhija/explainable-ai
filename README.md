# Explainable Decision Intelligence System

A Python-based system that computes eligibility decisions based on JSON rules and user input, providing detailed explanations.

## Setup

1.  **Clone/Open the repository.**
2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Start the Backend API

Run the FastAPI backend:
```bash
python -m uvicorn api:app --reload
```
The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`.

### 2. Start the Frontend UI

Run the Streamlit app:
```bash
python -m streamlit run ui_app.py
```
The UI will open in your browser (usually `http://localhost:8501`).

## Example Usage

In the UI:
1.  Enter `700000` for Income.
2.  Enter `Delhi` for State.
3.  Enter `19` for Age.
4.  Click "Check Eligibility".

## Project Structure

- `rules/`: Contains JSON rule definitions.
- `api.py`: Backend API entry point.
- `ui_app.py`: Frontend application.
- `rules_loader.py`: Handles rule loading and validation.
- `rule_engine.py`: Core logic for rule evaluation.
- `scoring.py`: Computes eligibility and confidence scores.
- `vector_store.py`: Vector search for explanations.
- `explanations.py`: Explanation generator.
