from groq import Groq
from config import API_KEY, MODEL, MAX_HISTORY, SUMMARY_TRIGGER
from personas import get_persona
from sessions import load_session, save_session
from cost_tracker import CostTracker
from rag import build_rag_context, rag_available

client = Groq(api_key=API_KEY)

class Chatbot:
    def __init__(self, session_name, persona="default"):
        self.session_name  = session_name
        self.persona_name  = persona
        self.system_prompt = get_persona(persona)
        self.messages      = load_session(session_name)
        self.cost_tracker  = CostTracker()
        self.rag_mode      = False

    # ------------------------------------------------------------------ #
    #  Core chat                                                           #
    # ------------------------------------------------------------------ #

    def chat(self, user_input):
        # RAG: inject relevant notes if mode is on
        full_user_input = user_input
        if self.rag_mode and rag_available():
            context = build_rag_context(user_input)
            if context:
                full_user_input = (
                    f"Use the following notes to answer if relevant:\n\n"
                    f"{context}\n"
                    f"If the notes don't cover the question, use your own knowledge.\n"
                    f"User question: {user_input}"
                )

        self.messages.append({"role": "user", "content": full_user_input})

        # Auto-summarize if history is too long
        if len(self.messages) > SUMMARY_TRIGGER:
            self._summarize_history()

        # Build messages with system prompt at top
        recent = self.messages[-MAX_HISTORY:]
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + recent

        # Call Groq API --------------------
        response = client.chat.completions.create(
            model=MODEL,
            messages=full_messages
        )

        reply = response.choices[0].message.content
        self.cost_tracker.record(response.usage)

        self.messages.append({"role": "assistant", "content": reply})
        save_session(self.session_name, self.messages)

        return reply

    # ------------------------------------------------------------------ #
    #  Auto-summarize old history                                          #
    # ------------------------------------------------------------------ #

    def _summarize_history(self):
        half         = len(self.messages) // 2
        old_messages = self.messages[:half]
        self.messages = self.messages[half:]

        convo_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in old_messages
            if m["role"] != "system"
        )

        summary_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Summarize this conversation in 3-5 bullet points. "
                        "Keep key facts, decisions, and any code mentioned:\n\n"
                        + convo_text
                    )
                }
            ]
        )

        summary = summary_response.choices[0].message.content
        self.cost_tracker.record(summary_response.usage)

        self.messages.insert(0, {
            "role": "system",
            "content": f"Summary of earlier conversation:\n{summary}"
        })

        save_session(self.session_name, self.messages)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def toggle_rag(self):
        if not rag_available():
            return False
        self.rag_mode = not self.rag_mode
        return True

    def clear(self):
        self.messages = []
        save_session(self.session_name, self.messages)

    def cost_summary(self):
        return self.cost_tracker.summary()