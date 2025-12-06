import requests
import openai
import re
import json

def persona_tone_instructions(persona: str):
    persona = persona.lower()

    tones = {
        "pastor": "Write with the compassionate, Scripture-centered tone of a caring pastor.",
        "teacher": "Explain concepts clearly and logically, like a Bible teacher guiding a class.",
        "counselor": "Respond with empathy, emotional warmth, and supportive Christian counseling.",
        "plain": "Write simply and clearly in everyday language, without church jargon.",
        "friend": "Speak like a supportive Christian friend offering encouragement.",
        "devotional": "Write in a reflective, devotional style that encourages meditation and application.",
        "layperson": "Explain everything in simple everyday terms as if speaking to someone new to Bible study."
    }

    return tones.get(persona, "")

# Bible API base
BIBLE_API_BASE = "https://bible-api.com"


# ============================================================
# 1) CLEAN, ROBUST REFERENCE PARSER
# ============================================================

def parse_reference(ref: str):
    """
    Extract book, chapter, and verse from references like:
    'John 3:16', '1 Corinthians 10:13', 'Psalm 34:18-19'
    Defaults to verse 1 if missing.
    Returns ("Unknown", 0, 0) only if completely unparsable.
    """
    ref = ref.strip().replace(".", "").replace(",", "")

    # Full match -> Book + Chapter:Verse
    match = re.match(r"([\dA-Za-z\s]+)\s(\d+):(\d+)", ref)
    if match:
        book, chapter, verse = match.groups()
        return book.strip(), int(chapter), int(verse)

    # Case: only Book + Chapter (Psalm 34)
    match = re.match(r"([\dA-Za-z\s]+)\s(\d+)$", ref)
    if match:
        book, chapter = match.groups()
        return book.strip(), int(chapter), 1

    # Unrecognized format
    return ("Unknown", 0, 0)


# ============================================================
# 2) FETCH VERSES (OpenAI → references → Bible API)
# ============================================================

def fetch_verses_for_topic(topic: str, translation: str = "kjv", max_results=6):
    """
    Uses OpenAI to generate relevant verse references,
    then fetches actual verses from the Bible API.
    """

    # --- Step 1: Ask OpenAI for references ---
    prompt = (
        "You are a biblical reference assistant. "
        f"Given a topic, list up to {max_results} Bible verse references "
        "(e.g., 'John 3:16', 'Ephesians 4:32'). "
        "Return ONLY the references separated by commas.\n\n"
        f"Topic: {topic}\nReferences:"
    )

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.0,
    )

    text = resp["choices"][0]["message"]["content"].strip()
    refs = [chunk.strip() for chunk in text.replace("\n", ",").split(",") if chunk.strip()]
    refs = refs[:max_results]

    # --- Step 2: Fetch verses from the Bible API ---
    verses = []

    for r in refs:
        try:
            url = f"{BIBLE_API_BASE}/{requests.utils.quote(r)}"
            q = {"translation": translation} if translation else {}

            r_resp = requests.get(url, params=q, timeout=10)
            r_resp.raise_for_status()

            data = r_resp.json()

            if "text" in data:
                text_body = data["text"].strip()
            elif "verses" in data:
                text_body = " ".join(v.get("text", "") for v in data["verses"]).strip()
            else:
                text_body = ""

            book, chapter, verse = parse_reference(r)

            verses.append({
                "book": book,
                "chapter": chapter,
                "verse": verse,
                "text": text_body
            })

        except Exception as e:
            book, chapter, verse = parse_reference(r)
            verses.append({
                "book": book,
                "chapter": chapter,
                "verse": verse,
                "text": f"[Error fetching verse: {str(e)}]"
            })

    # --- Step 3: Cleanup (remove bad entries) ---
    verses = [
        v for v in verses
        if v["book"] != "Unknown" and v["text"].strip() != ""
    ]

    return verses


# ============================================================
# 3) SUMMARY + COMMENTARY GENERATION
# ============================================================

def summarize_and_contextualize(question: str, verses: list, persona: str, want_commentary: bool):
    """
    Creates a structured summary with optional commentary using OpenAI.
    Applies persona tone instructions for tailored writing style.
    """

    # Merge verse texts
    verse_text_bundle = "\n\n".join(
        f"{v['book']} {v['chapter']}:{v['verse']} - {v['text']}"
        for v in verses
    )

    # Tone instructions from helper
    tone = persona_tone_instructions(persona)

    # Optional commentary block
    commentary_instruction = (
        "Include a short commentary (2–4 sentences) from classical commentators such as Matthew Henry."
        if want_commentary
        else ""
    )

    # ============================
    #        MAIN PROMPT
    # ============================
    prompt = f"""
You are a careful Bible-study assistant.

USER QUESTION:
{question}

HERE ARE RELATED VERSES:
{verse_text_bundle}

TASKS:
1. Provide a concise summary (3–6 sentences) explaining how these verses address the question.
2. {commentary_instruction}

Tone instructions:
{tone}

Return ONLY valid JSON in this format:
{{
  "summary": "...",
  "commentary": "..."
}}
    """

    # OpenAI call
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350,
        temperature=0.2,
    )

    ai_text = resp["choices"][0]["message"]["content"].strip()

    # ============================
    #   CLEAN UP MODEL OUTPUT
    # ============================

    # Remove Markdown code fences
    if ai_text.startswith("```"):
        ai_text = ai_text.strip("`")
        ai_text = ai_text.replace("json", "").replace("JSON", "").strip()

    # Try direct JSON parse
    try:
        data = json.loads(ai_text)
        return data.get("summary", ""), data.get("commentary", "")
    except:
        pass

    # ============================
    #   FALLBACK MANUAL PARSING
    # ============================
    summary = ""
    commentary = ""

    if "commentary" in ai_text.lower():
        parts = re.split(r"(?i)commentary", ai_text, 1)
        summary = parts[0].replace("summary", "").strip()
        commentary = parts[1].strip()
    else:
        summary = ai_text.strip()

    return summary, commentary
