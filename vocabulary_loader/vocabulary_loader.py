import streamlit as st
import json
import boto3
import random
import os
from qdrant_client.http import models
from datetime import datetime
from utils.qdrant_utils import get_qdrant_client
import uuid

# Initialize Qdrant client
client = get_qdrant_client()

# Function to initialize the collections
def initialize_collections():
    try:
        # Check if collection exists first
        collections = client.get_collections().collections
        exists = any(collection.name == "words" for collection in collections)
        
        if not exists:
            # Collection for words
            client.create_collection(
                collection_name="words",
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
            st.success("Qdrant collection initialized successfully.")
        else:
            st.info("Collection 'words' already exists.")
    except Exception as e:
        st.error(f"Error with Qdrant collection: {e}")

# Initialize the collections
initialize_collections()

# Function to fetch all words from Qdrant
def fetch_words():
    try:
        search_result = client.scroll(
            collection_name="words",
            limit=100,  # Adjust as needed
            with_payload=True
        )
        words = [point.payload for point in search_result[0]]
        return words
    except Exception as e:
        st.error(f"Error fetching words: {e}")
        return []

# Function to add a word to Qdrant
def add_word(salish, english):
    try:
        # Generate a random integer ID
        point_id = random.randint(1, 2**31 - 1)  # Max 32-bit unsigned int
        client.upsert(
            collection_name="words",
            points=[
                models.PointStruct(
                    id=point_id,  # Using integer ID
                    payload={
                        "salish": salish,
                        "english": english,
                        "created_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            ]
        )
        st.success("Word added successfully!")
    except Exception as e:
        st.error(f"Error adding word: {e}")

# Function to update a word in Qdrant
def update_word(id, salish, english):
    try:
        client.upsert(
            collection_name="words",
            points=[
                models.PointStruct(
                    id=id,
                    payload={
                        "salish": salish,
                        "english": english,
                        "updated_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            ]
        )
        st.success("Word updated successfully!")
    except Exception as e:
        st.error(f"Error updating word: {e}")

# Function to delete a word from Qdrant
def delete_word(id):
    try:
        client.delete(
            collection_name="words",
            points_selector=models.PointIdsList(
                points=[id]
            )
        )
        st.success("Word deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting word: {e}")

def insert_words_into_db(words):
    try:
        points = []
        for word in words:
            # Generate a random integer ID for each word
            point_id = random.randint(1, 2**31 - 1)  # Max 32-bit unsigned int
            points.append(
                models.PointStruct(
                    id=point_id,  # Using integer ID
                    payload={
                        "salish": word['salish'],
                        "english": word['english'],
                        "created_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            )
        
        client.upsert(
            collection_name="words",
            points=points
        )
        st.success("All words added successfully!")
    except Exception as e:
        st.error(f"Error inserting words: {e}")

# Function to generate vocabulary using Amazon Bedrock
def generate_vocabulary(prompt):
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Initialize the AWS client
    boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    session = boto3.session.Session()
    
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

    model_id = "amazon.nova-lite-v1:0"
    content_type = "application/json"
    accept = "application/json"

    # Update prompt to generate only Salish and English translations
    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt + "Generate 10 words in the following format: ```Salish - English``` include only the words per line and no other information"}]
            }
        ]
    })

    try:
        response = bedrock_client.invoke_model(
            body=body,
            modelId=model_id,
            contentType=content_type,
            accept=accept
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        generated_text = response_body['output']['message']['content'][0]['text']
        words = parse_generated_text(generated_text)
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
        if len(parts) == 2:  # We expect 2 parts now: Salish and English
            salish = parts[0].strip()
            english = parts[1].strip()
            
            words.append({
                "salish": salish,
                "english": english
            })
    return words

# Streamlit UI
st.title("Salish Vocabulary Generator")

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
    new_salish = st.text_input("Salish")
    new_english = st.text_input("English")
    if st.button("Add Word"):
        if new_salish and new_english:
            add_word(new_salish, new_english)
            # Refresh the word list after adding
            words = fetch_words()
            st.table(words)
        else:
            st.warning("Please fill in all fields.")

    # Update word form
    st.subheader("Update Word")
    if words:
        word_to_update = st.selectbox(
            "Select word to update",
            options=words,
            format_func=lambda x: f"{x['salish']} - {x['english']}"
        )
        if word_to_update:
            update_salish = st.text_input("New Salish", value=word_to_update['salish'])
            update_english = st.text_input("New English", value=word_to_update['english'])
            if st.button("Update"):
                if update_salish and update_english:
                    update_word(word_to_update['id'], update_salish, update_english)
                    # Refresh the word list after updating
                    words = fetch_words()
                    st.table(words)
                else:
                    st.warning("Please fill in all fields.")

    # Delete word form
    st.subheader("Delete Word")
    if words:
        word_to_delete = st.selectbox(
            "Select word to delete",
            options=words,
            format_func=lambda x: f"{x['salish']} - {x['english']}"
        )
        if word_to_delete and st.button("Delete"):
            delete_word(word_to_delete['id'])
            # Refresh the word list after deleting
            words = fetch_words()
            st.table(words)

elif operation == "Import/Export":
    st.header("Import/Export Vocabulary")

    # Export
    st.subheader("Export Vocabulary")
    if st.button("Export to JSON"):
        words = fetch_words()
        if words:
            json_data = json.dumps(words, indent=4, ensure_ascii=False)
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
        try:
            json_data = json.loads(uploaded_file.read().decode("utf-8"))
            st.write("Imported Words:")
            st.json(json_data)
            if st.button("Add Imported Words to Database"):
                insert_words_into_db(json_data)
                words = fetch_words()
                st.table(words)
        except json.JSONDecodeError:
            st.error("Invalid JSON format.")
