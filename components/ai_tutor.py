import os
def explain_with_ai(prompt, context="Networking", level="Beginner"):
    key=None
    try:
        import streamlit as st
        key=st.secrets.get("OPENAI_API_KEY")
    except Exception: pass
    key=key or os.getenv("OPENAI_API_KEY")
    if not key:
        return ("**Offline tutor mode:** No OpenAI API key is configured.\n\n"
                f"**Context:** {context}\n\n**Question:** {prompt}\n\n"
                "Start with the definition, identify the OSI layer and endpoints, then trace the message step by step. "
                "Use the official references in this lesson for exact standards details.")
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        result=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),
          input=[{"role":"system","content":f"You are a precise networking and defensive cybersecurity tutor. Explain at {level} level. Distinguish standards from examples, never invent ports or RFC requirements, and require authorised labs. Context: {context}."},
                 {"role":"user","content":prompt}])
        return result.output_text
    except Exception as exc:
        return f"AI service unavailable; app remains usable. Error type: {type(exc).__name__}"
