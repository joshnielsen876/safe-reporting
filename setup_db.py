import sqlite3

# Define database file path (adjust if needed)
DB_PATH = "/Workspace/Users/ag95@cdc.gov/Llama index test/Safe reporting guidelines/articles.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define schema based on our discussion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        name_of_deceased TEXT,
        date_of_death DATE,
        headline TEXT,
        article_text TEXT,
        date_of_publication DATE,
        protective BOOLEAN,
        neutral BOOLEAN,
        sensational BOOLEAN,
        harmful BOOLEAN,
        headline_reasoning TEXT,
        suicide_framing FLOAT,
        factual_information FLOAT,
        non_stigmatizing_language FLOAT,
        method_and_scene FLOAT,
        suicide_note FLOAT,
        factors_and_reasons FLOAT,
        sensationalized FLOAT,
        glamorized FLOAT,
        resources FLOAT,
        TEMPOS reasoning TEXT,
        normalized_tempos_score FLOAT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database and table created successfully!")

if __name__ == "__main__":
    create_database()
