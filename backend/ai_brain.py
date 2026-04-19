from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Admission assistant for HBTU (Harcourt Butler Technical University), Kanpur.

STRICT RULES:
1. ONLY answer questions related to HBTU admissions, B.Tech/MBA counselling, JEE/CUET/CAT process.
2. If question is outside this scope, say: "I can only help with HBTU admissions and counselling queries."
3. NEVER make up rank cutoffs, seat numbers, fee amounts or dates. If unsure, say: 
   "I don't have reliable data on this — please check hbtu.ac.in."
4. Keep responses concise and use bullet points where helpful."""


def ai_brain_response(user_message: str, conversation_history: list, user_context: dict) -> str:
    context_note = f"\n[User context captured so far: {user_context}]" if user_context else ""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += conversation_history[-6:]  # last 3 turns
    messages.append({"role": "user", "content": user_message + context_note})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # free, very capable
            messages=messages,
            max_tokens=512,
            temperature=0.3   # lower = less creative = less hallucination
        )
        return response.choices[0].message.content

    except Exception as e:
        return "I'm having trouble right now. Please ask about rank prediction, seats, or counselling process."