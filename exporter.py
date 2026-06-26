import os
from datetime import datetime
from config import EXPORTS_DIR

os.makedirs(EXPORTS_DIR, exist_ok=True)

def export_markdown(session_name, messages, persona):
    """Export conversation as a clean markdown file."""
    filename = f"{session_name}_{datetime.now().strftime('%H%M%S')}.md"
    path = os.path.join(EXPORTS_DIR, filename)

    with open(path, "w") as f:
        f.write(f"# Chat Export — {session_name}\n")
        f.write(f"**Persona:** {persona}  \n")
        f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Messages:** {len(messages)}\n\n")
        f.write("---\n\n")

        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            if role == "User":
                f.write(f"**You:** {content}\n\n")
            elif role == "Assistant":
                f.write(f"**Bot:** {content}\n\n")
                f.write("---\n\n")

    return path