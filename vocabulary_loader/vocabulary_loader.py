import streamlit as st
import json
import sqlite3
import boto3
import random
import os

# Database connection (replace with your actual database path)
DATABASE_PATH = '../my-learning-api/language_learning.db'

# Function to connect to the database
def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Function to initialize the database
def initialize_db():
    conn = connect_db()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kanji TEXT NOT NULL,
                romaji TEXT NOT NULL,
                english TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Database initialized and table created.")
    except Exception as e:
        st.error(f"Error initializing database: {e}")
    finally:
        conn.close()

# Initialize the database
initialize_db()

# Function to fetch all words from the database
def fetch_words():
    conn = connect_db()
    try:
        cursor = conn.execute("SELECT * FROM words")
        words = [dict(row) for row in cursor.fetchall()]
        return words
    except Exception as e:
        st.error(f"Error fetching words: {e}")
        return []
    finally:
        conn.close()

# Function to add a word to the database
def add_word(kanji, romaji, salish, navajo, english):
    conn = connect_db()
    try:
        conn.execute(
            "INSERT INTO words (kanji, romaji, salish, navajo, english) VALUES (?, ?, ?, ?, ?)",
            (kanji, romaji, salish, navajo, english)
        )
        conn.commit()
        st.success("Word added successfully!")
    except Exception as e:
        st.error(f"Error adding word: {e}")
    finally:
        conn.close()

# Function to update a word in the database
def update_word(id, kanji, romaji, salish, navajo, english):
    conn = connect_db()
    try:
        conn.execute(
            "UPDATE words SET kanji=?, romaji=?, salish=?, navajo=?, english=? WHERE id=?",
            (kanji, romaji, salish, navajo, english, id)
        )
        conn.commit()
        st.success("Word updated successfully!")
    except Exception as e:
        st.error(f"Error updating word: {e}")
    finally:
        conn.close()

# Function to delete a word from the database
def delete_word(id):
    conn = connect_db()
    try:
        conn.execute("DELETE FROM words WHERE id=?", (id,))
        conn.commit()
        st.success("Word deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting word: {e}")
    finally:
        conn.close()

def insert_words_into_db(words):
    conn = connect_db()
    try:
        for word in words:
            add_word(word['kanji'], word['romaji'], word['salish'], word['navajo'], word['english'])
        st.success("All words added successfully!")
    except Exception as e:
        st.error(f"Error inserting words: {e}")
    finally:
        conn.close()

# Function to generate vocabulary using Amazon Bedrock
def generate_vocabulary(prompt):
    session = boto3.session.Session()
    region = "us-east-1"
    
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name=region
    )

    model_id = "amazon.nova-lite-v1:0"
    content_type = "application/json"
    accept = "application/json"

    # Construct the request body using "messages"
    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt + "Generate 10 words in the following format: ```kanji - romaji - Salish - Navajo - english``` include only the words per line and no other information"}]
            }
        ]
    })

    print("Request Body:")
    print(body)

    try:
        response = bedrock_client.invoke_model(
            body=body,
            modelId=model_id,
            contentType=content_type,
            accept=accept
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        

        # Extract the generated text from the response
        generated_text = response_body['output']['message']['content'][0]['text']  # Adjusted to match the response structure
        print(generated_text)
        # Parse the generated text into a list of words (kanji, romaji, english)
        words = parse_generated_text(generated_text)
        # Insert the parsed words into the database
        insert_words_into_db(words)
        return words

    except Exception as e:
        st.error(f"Error calling Bedrock: {e}")
        return []

def parse_generated_text(generated_text):
    words = []
    for line in generated_text.split('\n'):
        if not line.strip():
            continue
        
        parts = line.split(' - ')
        if len(parts) == 5:  # We expect 5 parts now: kanji, romaji, Salish, Navajo, english
            kanji = parts[0].strip()
            romaji = parts[1].strip()
            salish = parts[2].strip()
            navajo = parts[3].strip()
            english = parts[4].strip()
            
            words.append({
                "kanji": kanji,
                "romaji": romaji,
                "salish": salish,
                "navajo": navajo,
                "english": english
            })
    return words


# Function to export vocabulary to JSON
def export_to_json(words):
    return json.dumps(words, indent=4, ensure_ascii=False)

# Function to import vocabulary from JSON
def import_from_json(json_data):
    try:
        words = json.loads(json_data)
        return words
    except json.JSONDecodeError:
        st.error("Invalid JSON format.")
        return None

# Streamlit UI
st.title("Vocabulary Generator")

# Sidebar options
operation = st.sidebar.selectbox("Choose an operation", ["Generate", "CRUD", "Import/Export"])

if operation == "Generate":
    st.header("Generate Vocabulary")
    prompt = st.text_area("Enter a prompt for vocabulary generation")
    if st.button("Generate"):
        if prompt:
            generated_words = generate_vocabulary(prompt)
            st.write("Generated Words:")
            st.json(generated_words)
        else:
            st.warning("Please enter a prompt.")

elif operation == "CRUD":
    st.header("CRUD Operations")
    words = fetch_words()

    # Display words in a table
    if words:
        st.write("Existing Words:")
        st.table(words)
    else:
        st.info("No words found in the database.")

    # Add word form
    st.subheader("Add New Word")
    new_kanji = st.text_input("Kanji")
    new_romaji = st.text_input("Romaji")
    new_english = st.text_input("English")
    if st.button("Add Word"):
        if new_kanji and new_romaji and new_english:
            add_word(new_kanji, new_romaji, new_english)
            # Refresh the word list after adding
            words = fetch_words()
            st.table(words)
        else:
            st.warning("Please fill in all fields.")

    # Update word form
    st.subheader("Update Word")
    update_id = st.number_input("Enter ID of word to update", min_value=1, step=1)
    update_kanji = st.text_input("New Kanji")
    update_romaji = st.text_input("New Romaji")
    update_english = st.text_input("New English")
    if st.button("Update"):
        if update_id and update_kanji and update_romaji and update_english:
            update_word(update_id, update_kanji, update_romaji, update_english)
            # Refresh the word list after updating
            words = fetch_words()
            st.table(words)
        else:
            st.warning("Please fill in all fields.")

    # Delete word form
    st.subheader("Delete Word")
    delete_id = st.number_input("Enter ID of word to delete", min_value=1, step=1)
    if st.button("Delete"):
        if delete_id:
            delete_word(delete_id)
            # Refresh the word list after deleting
            words = fetch_words()
            st.table(words)
        else:
            st.warning("Please enter the ID of the word to delete.")

elif operation == "Import/Export":
    st.header("Import/Export Vocabulary")

    # Export
    st.subheader("Export Vocabulary")
    if st.button("Export to JSON"):
        words = fetch_words()
        if words:
            json_data = export_to_json(words)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="vocabulary.json",
                mime="application/json",
            )
        else:
            st.info("No words to export.")

    # Import
    st.subheader("Import Vocabulary")
    uploaded_file = st.file_uploader("Upload a JSON file", type=["json"])
    if uploaded_file is not None:
        json_data = uploaded_file.read().decode("utf-8")
        imported_words = import_from_json(json_data)
        if imported_words:
            st.write("Imported Words:")
            st.json(imported_words)
            # Option to add imported words to the database
            if st.button("Add Imported Words to Database"):
                conn = connect_db()
                try:
                    for word in imported_words:
                        conn.execute("INSERT INTO words (kanji, romaji, english) VALUES (?, ?, ?)",
                                     (word['kanji'], word['romaji'], word['english']))
                    conn.commit()
                    st.success("Imported words added to the database!")
                    words = fetch_words()
                    st.table(words)
                except Exception as e:
                    st.error(f"Error adding imported words: {e}")
                finally:
                    conn.close()

# The following is needed for the boto3 library to function correctly
os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = '' 