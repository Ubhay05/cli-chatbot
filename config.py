import os

# --- API Settings ---
API_KEY = os.getenv("GROQ_API_KEY", "groq-key-here") # to avoid key exposure set in terminal
MODEL   = "llama-3.1-8b-instant"  

# --- Summarization ---
MAX_HISTORY     = 20
SUMMARY_TRIGGER = 15

# --- Groq Pricing (completely free on free tier) ---
INPUT_COST_PER_1K  = 0.0
OUTPUT_COST_PER_1K = 0.0
USD_TO_INR         = 83.0

# --- Paths ---
DATA_DIR     = "data"
SESSIONS_DIR = "data/sessions"
EXPORTS_DIR  = "data/exports"
NOTES_DIR    = "data/notes"
VECTOR_STORE = "data/vector_store"