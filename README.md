# CLI Chatbot — AI Terminal Chatbot in Python

A feature-rich terminal chatbot built with Python and Groq API (Llama 3) with RAG, multi-session management, personas and cost tracking.

## Features
- 5 switchable personas — default, coding, study, interview, debug
- Multiple named sessions with persistent JSON storage
- RAG mode — answers questions from your own notes using TF-IDF vectors and cosine similarity
- Auto-summarization when conversation history exceeds token limits
- Cost tracker — monitors per-session token usage and estimated API cost
- Export conversations as markdown files

## Setup

```bash
conda create -n chatbot python=3.11 -y
conda activate chatbot
pip install -r requirements.txt
export GROQ_API_KEY="your-key-here"
python main.py
```

## Commands

| Command | What it does |
|---|---|
| help | Show all commands |
| clear | Clear current session |
| cost | Show token usage |
| export | Save chat as markdown |
| rag on/off | Toggle notes mode |
| index | Index your notes |
| sessions | List saved sessions |
| new name | Start new session |
| load name | Load old session |
| persona name | Switch persona |
| quit | Exit and show stats |

## RAG Setup

Add your notes as .txt files to data/notes/ then inside chatbot run index and rag on

## Architecture

main.py → CLI loop and commands
chatbot.py → Groq API calls and history
rag.py → TF-IDF vectors and cosine similarity
personas.py → 5 system prompts
sessions.py → JSON session management
cost_tracker.py → token tracking
exporter.py → markdown export
config.py → settings
