import os
import json
import sqlite3
import time
from datetime import datetime
from openai import OpenAI

# Ensure API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "\u274c OPENAI_API_KEY is not set. Please load your .env file or export the key."
    )

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

audio_dir = "data/patient_conversations"
db_path = "baymax_agentx_health.db"


def transcribe_audio_openai(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text"
        )
    return response


def extract_structured_symptoms(transcript):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical assistant extracting structured symptoms from a doctor-patient conversation.",
            },
            {
                "role": "user",
                "content": f"""Given this transcript, extract the symptoms mentioned by the patient.

Return:
- Symptom name
- Onset (if any)
- Severity (if any)
- Associated details (triggers, relief, duration)

Also identify the **primary symptom** the conversation focuses on.

Respond ONLY in this JSON format:

{{
  "primary_symptom": {{
    "symptom": "...",
    "onset": "...",
    "severity": "...",
    "associated": ["...", "..."]
  }},
  "all_symptoms": [
    {{
      "symptom": "...",
      "onset": "...",
      "severity": "...",
      "associated": ["..."]
    }},
    ...
  ]
}}

Transcript:
{transcript}""",
            },
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def generate_physician_summary(transcript):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You summarize clinical conversations into physician-friendly notes.",
            },
            {
                "role": "user",
                "content": f"""Summarize the following doctor-patient conversation for a physician.

                Include:
                - Chief complaint
                - Symptom onset, severity, progression
                - Pertinent lifestyle/medical history
                - Keep it concise, clinical, and objective

                Transcript:
                {transcript}""",
            },
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def list_audio_files_for_patient(patient_id):
    files = sorted(
        f
        for f in os.listdir(audio_dir)
        if f.startswith(patient_id) and f.endswith(".mp3")
    )
    return files


def is_duplicate(user_id, audio_file):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1 FROM summary WHERE user_id = ? AND audio_file = ?
    """,
        (user_id, audio_file),
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def fetch_existing_summary_and_symptoms(user_id, audio_file):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT transcript_text, summary_text FROM summary
        WHERE user_id = ? AND audio_file = ?
    """,
        (user_id, audio_file),
    )
    summary_row = cursor.fetchone()

    cursor.execute(
        """
        SELECT symptom_details FROM symptoms
        WHERE user_id = ? AND audio_file = ?
    """,
        (user_id, audio_file),
    )
    symptoms_row = cursor.fetchone()

    conn.close()

    return {
        "patient_id": user_id,
        "transcript": summary_row[0] if summary_row else "",
        "physician_summary": summary_row[1] if summary_row else "",
        "symptoms_json": symptoms_row[0] if symptoms_row else "",
    }


def process_audio_to_symptoms_and_summary(audio_path, patient_id="Unknown"):
    import sqlite3
    from datetime import datetime
    import os

    audio_filename = os.path.basename(audio_path)

    print(f"🔊 Processing {audio_filename}...")

    # Step 0: Check if result already exists in DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ✅ Create tables if not exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS summary (
            user_id TEXT,
            recorded_datetime TEXT,
            audio_file TEXT,
            transcript_text TEXT,
            summary_text TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS symptoms (
            user_id TEXT,
            recorded_datetime TEXT,
            audio_file TEXT,
            primary_symptoms TEXT,
            secondary_symptoms TEXT,
            symptom_details TEXT,
            alert_flag BOOLEAN
        )
    """
    )

    cursor.execute(
        """
        SELECT transcript_text, summary_text FROM summary
        WHERE user_id = ? AND audio_file = ?
    """,
        (patient_id, audio_filename),
    )
    summary_row = cursor.fetchone()

    cursor.execute(
        """
        SELECT symptom_details FROM symptoms
        WHERE user_id = ? AND audio_file = ?
    """,
        (patient_id, audio_filename),
    )
    symptom_row = cursor.fetchone()

    conn.close()

    if summary_row and symptom_row:
        print(
            f"🔄 Skipping processing. Fetching stored results for {audio_filename}..."
        )

        return {
            "patient_id": patient_id,
            "audio_file": audio_filename,
            "transcript": summary_row[0],
            "physician_summary": summary_row[1],
            "symptoms_json": symptom_row[0],
        }

    # Step 1: Transcribe
    transcript = transcribe_audio_openai(audio_path)
    print("✅ Transcription complete.")

    # Step 2: Extract structured symptoms
    structured_symptoms = extract_structured_symptoms(transcript)
    print("✅ Symptoms extracted.")

    # Step 3: Generate physician summary
    summary = generate_physician_summary(transcript)
    print("✅ Physician summary generated.")

    # Step 4: Return all results
    return {
        "patient_id": patient_id,
        "audio_file": audio_filename,
        "transcript": transcript,
        "physician_summary": summary,
        "symptoms_json": structured_symptoms,
    }


def store_results_in_sqlite(results, db_path="baymax_agentx_health.db"):
    patient_id = results["patient_id"]
    transcript_text = results["transcript"]
    summary_text = results["physician_summary"]
    symptoms_json = results["symptoms_json"]
    audio_file = results["audio_file"]
    recorded_datetime = datetime.now().isoformat()

    # 🧠 Parse symptoms JSON
    try:
        if isinstance(symptoms_json, str):
            symptoms_json = symptoms_json.strip()
            if symptoms_json.startswith("```json"):
                symptoms_json = (
                    symptoms_json.replace("```json", "").replace("```", "").strip()
                )
            parsed = json.loads(symptoms_json)
        elif isinstance(symptoms_json, dict):
            parsed = symptoms_json
        else:
            raise ValueError("symptoms_json is not in a valid format")

        primary_symptom = parsed["primary_symptom"]["symptom"]
        all_symptoms = parsed.get("all_symptoms", [])
        secondary_symptoms = [
            s["symptom"] for s in all_symptoms if s["symptom"] != primary_symptom
        ]
        alert_flag = any(
            s.lower() in ["chest pain", "shortness of breath"]
            for s in [primary_symptom] + secondary_symptoms
        )
        symptom_details = json.dumps(parsed)

    except Exception as e:
        print(f"❌ Failed to parse symptoms JSON: {e}")
        print("🔍 Raw symptoms_json value was:\n", symptoms_json)
        return

    # 🔁 Retry-safe DB write with duplicate check
    for attempt in range(3):
        try:
            conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
            cursor = conn.cursor()

            # ✅ Check for existing record
            cursor.execute(
                """
                SELECT 1 FROM summary WHERE user_id = ? AND audio_file = ?
            """,
                (patient_id, audio_file),
            )
            if cursor.fetchone():
                print(
                    f"⚠️ Entry already exists for {patient_id} - {audio_file}. Skipping insert."
                )
                return

            # Insert into summary
            cursor.execute(
                """
                INSERT INTO summary (user_id, recorded_datetime, audio_file, transcript_text, summary_text)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    patient_id,
                    recorded_datetime,
                    audio_file,
                    transcript_text,
                    summary_text,
                ),
            )

            # Insert into symptoms
            cursor.execute(
                """
                INSERT INTO symptoms (user_id, recorded_datetime, audio_file, primary_symptoms, secondary_symptoms, symptom_details, alert_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    patient_id,
                    recorded_datetime,
                    audio_file,
                    primary_symptom,
                    json.dumps(secondary_symptoms),
                    symptom_details,
                    int(alert_flag),
                ),
            )

            conn.commit()
            print(f"✅ Stored results for {patient_id} ({audio_file}) into {db_path}")
            break  # ✅ Success

        except sqlite3.OperationalError as e:
            print(f"🔁 Retry {attempt + 1}/3 - SQLite OperationalError: {e}")
            time.sleep(2)

        finally:
            try:
                conn.close()
            except:
                pass
    print(f"✅ Stored results for {audio_file} into {db_path}")
