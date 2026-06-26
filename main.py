import os
from chatbot import Chatbot
from personas import list_personas
from sessions import list_sessions, delete_session, new_session_name
from exporter import export_markdown
from rag import index_notes, rag_available
from config import NOTES_DIR

# ------------------------------------------------------------------ #
#  Terminal colors (no extra library needed)                          #
# ------------------------------------------------------------------ #
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    BLUE   = "\033[94m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"

def user_print(text):
    print(f"{C.BLUE}{C.BOLD}You:{C.RESET} {text}")

def bot_print(text):
    print(f"\n{C.GREEN}{C.BOLD}Bot:{C.RESET} {text}\n")

def info(text):
    print(f"{C.CYAN}  ➜  {text}{C.RESET}")

def warn(text):
    print(f"{C.YELLOW}  ⚠  {text}{C.RESET}")

def error(text):
    print(f"{C.RED}  ✗  {text}{C.RESET}")

# ------------------------------------------------------------------ #
#  Help text                                                          #
# ------------------------------------------------------------------ #
HELP = f"""
{C.BOLD}Commands:{C.RESET}
  {C.CYAN}help{C.RESET}               Show this message
  {C.CYAN}clear{C.RESET}              Clear current session history
  {C.CYAN}cost{C.RESET}               Show token usage and cost (INR + USD)
  {C.CYAN}export{C.RESET}             Export conversation as markdown file
  {C.CYAN}rag on/off{C.RESET}         Toggle RAG mode (answers from your notes)
  {C.CYAN}index{C.RESET}              Index your notes in data/notes/*.txt
  {C.CYAN}sessions{C.RESET}           List all saved sessions
  {C.CYAN}new <name>{C.RESET}         Start a new session with given name
  {C.CYAN}load <name>{C.RESET}        Load an existing session
  {C.CYAN}delete <name>{C.RESET}      Delete a saved session
  {C.CYAN}persona <name>{C.RESET}     Switch persona mid-conversation
  {C.CYAN}personas{C.RESET}           List available personas
  {C.CYAN}quit{C.RESET}               Exit and show cost summary
"""

# ------------------------------------------------------------------ #
#  Setup                                                              #
# ------------------------------------------------------------------ #

def choose_persona():
    personas = list_personas()
    print(f"\n{C.BOLD}Available personas:{C.RESET} {', '.join(personas)}")
    choice = input(f"{C.GRAY}Choose persona (Enter = default): {C.RESET}").strip()
    return choice if choice in personas else "default"

def choose_session():
    sessions = list_sessions()
    if sessions:
        print(f"\n{C.BOLD}Saved sessions:{C.RESET} {', '.join(sessions)}")
        name = input(f"{C.GRAY}Session name (Enter = new session): {C.RESET}").strip()
        if name in sessions:
            return name
    auto_name = new_session_name()
    info(f"Starting new session: {auto_name}")
    return auto_name

# ------------------------------------------------------------------ #
#  Main loop                                                          #
# ------------------------------------------------------------------ #

def main():
    os.system("clear" if os.name == "posix" else "cls")
    print(f"\n{C.BOLD}{C.CYAN}╔══════════════════════════════╗")
    print(f"║     CLI Chatbot  v2.0        ║")
    print(f"╚══════════════════════════════╝{C.RESET}\n")

    persona      = choose_persona()
    session_name = choose_session()
    bot          = Chatbot(session_name=session_name, persona=persona)

    print(f"\n{C.BOLD}Session:{C.RESET} {session_name}  |  "
          f"{C.BOLD}Persona:{C.RESET} {persona}  |  "
          f"{C.BOLD}RAG:{C.RESET} {'ON' if bot.rag_mode else 'OFF'}")
    print(f"{C.GRAY}Type 'help' for commands{C.RESET}\n")
    print("─" * 40)

    while True:
        try:
            user_input = input(f"\n{C.BLUE}{C.BOLD}You:{C.RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            user_input = "quit"

        if not user_input:
            continue

        # ── commands ──────────────────────────────────────────────
        lower = user_input.lower()

        if lower == "quit":
            print(bot.cost_summary())
            info("Goodbye!")
            break

        elif lower == "help":
            print(HELP)

        elif lower == "clear":
            bot.clear()
            info("Session history cleared.")

        elif lower == "cost":
            print(bot.cost_summary())

        elif lower == "export":
            path = export_markdown(session_name, bot.messages, persona)
            info(f"Exported to: {path}")

        elif lower == "index":
            info(f"Indexing notes from {NOTES_DIR}/...")
            index_notes()

        elif lower.startswith("rag"):
            parts = lower.split()
            if len(parts) == 2 and parts[1] == "on":
                if rag_available():
                    bot.rag_mode = True
                    info("RAG mode ON — answers will use your notes.")
                else:
                    warn("No index found. Run 'index' first to index your notes.")
            elif len(parts) == 2 and parts[1] == "off":
                bot.rag_mode = False
                info("RAG mode OFF.")
            else:
                info(f"RAG is currently {'ON' if bot.rag_mode else 'OFF'}. Use 'rag on' or 'rag off'.")

        elif lower == "sessions":
            sessions = list_sessions()
            if sessions:
                info("Saved sessions: " + ", ".join(sessions))
            else:
                info("No saved sessions yet.")

        elif lower.startswith("new "):
            new_name = user_input[4:].strip()
            if new_name:
                session_name = new_name
                bot = Chatbot(session_name=session_name, persona=persona)
                info(f"New session started: {session_name}")
            else:
                warn("Usage: new <session_name>")

        elif lower.startswith("load "):
            name = user_input[5:].strip()
            sessions = list_sessions()
            if name in sessions:
                session_name = name
                bot = Chatbot(session_name=session_name, persona=persona)
                info(f"Loaded session: {session_name} ({len(bot.messages)} messages)")
            else:
                error(f"Session '{name}' not found. Use 'sessions' to list all.")

        elif lower.startswith("delete "):
            name = user_input[7:].strip()
            if delete_session(name):
                info(f"Deleted session: {name}")
            else:
                error(f"Session '{name}' not found.")

        elif lower == "personas":
            info("Available personas: " + ", ".join(list_personas()))

        elif lower.startswith("persona "):
            new_persona = user_input[8:].strip()
            if new_persona in list_personas():
                persona = new_persona
                bot.persona_name  = persona
                bot.system_prompt = __import__("personas").get_persona(persona)
                info(f"Switched to persona: {persona}")
            else:
                error(f"Unknown persona '{new_persona}'. Use 'personas' to list all.")

        # ── normal chat ───────────────────────────────────────────
        else:
            try:
                reply = bot.chat(user_input)
                bot_print(reply)
            except Exception as e:
                error(f"API error: {e}")

if __name__ == "__main__":
    main()