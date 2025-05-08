import os
import sqlite3

DB_PATH = os.getenv("DB_PATH")


def refresh_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop and recreate summary table
    print("⚠️ Dropping existing 'summary' table (if it exists)...")
    cursor.execute("DROP TABLE IF EXISTS summary")

    print("✅ Creating new 'summary' table...")
    cursor.execute(
        """
        CREATE TABLE summary (
            user_id TEXT,
            recorded_datetime TEXT,
            audio_file TEXT,
            transcript_text TEXT,
            summary_text TEXT
        )
    """
    )

    # Drop and recreate symptoms table
    print("⚠️ Dropping existing 'symptoms' table (if it exists)...")
    cursor.execute("DROP TABLE IF EXISTS symptoms")

    print("✅ Creating new 'symptoms' table...")
    cursor.execute(
        """
        CREATE TABLE symptoms (
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

    conn.commit()
    conn.close()
    print("\n✅ Both 'summary' and 'symptoms' tables have been refreshed.")


if __name__ == "__main__":
    refresh_tables()
    print("🔄 Tables refreshed successfully.")
    print("You can now re-run the audio processing pipeline to store new results.")
    print("🔄 Tables refreshed successfully.")
