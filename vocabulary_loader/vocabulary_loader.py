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

# Define supported languages
SUPPORTED_LANGUAGES = ["salish", "italian"]

# Function to initialize the collections
def initialize_collections():
    try:
        # Check if collection exists first
        collections = client.get_collections().collections
        exists = any(collection.name == "words" for collection in collections)
        
        if not exists:
            # Collection for words
            client.recreate_collection( # Use recreate for potential schema updates
                collection_name="words",
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
            # Ensure payload indexes exist (including the new language field)
            try:
                client.create_payload_index(collection_name="words", field_name="language", field_schema=models.PayloadSchemaType.KEYWORD)
                client.create_payload_index(collection_name="words", field_name="target_word", field_schema=models.PayloadSchemaType.TEXT) # Index target word
                client.create_payload_index(collection_name="words", field_name="english", field_schema=models.PayloadSchemaType.TEXT)
                st.success("Qdrant collection 'words' initialized/verified with necessary indexes.")
            except Exception as index_e:
                st.warning(f"Could not create indexes (they might exist): {index_e}")
        else:
            st.info("Collection 'words' already exists. Ensure indexes are correct.")
    except Exception as e:
        st.error(f"Error with Qdrant collection: {e}")

# Initialize the collections
initialize_collections()

# Function to fetch all words from Qdrant
def fetch_words():
    try:
        # Scroll through all points, fetching payload including language
        search_result, _ = client.scroll(
            collection_name="words",
            limit=1000,  # Increase limit to fetch more/all words if needed
            with_payload=True,
            with_vectors=False
        )
        # Ensure payload is dictionary and add default language if missing (for backward compatibility)
        words = []
        for point in search_result:
            payload = point.payload
            if isinstance(payload, dict):
                # Add id from the point itself into the payload for easier reference
                payload['id'] = point.id 
                # Handle potential legacy data without language
                if 'language' not in payload:
                    payload['language'] = 'salish' # Assume old data is Salish
                # Rename 'salish' to 'target_word' if present
                if 'salish' in payload and 'target_word' not in payload:
                    payload['target_word'] = payload.pop('salish')
                elif 'target_word' not in payload:
                    payload['target_word'] = "[missing]" # Placeholder if somehow missing
                words.append(payload)
            else:
                st.warning(f"Skipping point with non-dict payload: {point.id}")

        return words
    except Exception as e:
        st.error(f"Error fetching words: {e}")
        return []

# Add this function to check for duplicates, now language-aware
def is_duplicate_word(target_word: str, english: str, language: str, existing_words: list) -> bool:
    """Check if a word already exists in the collection for the specific language."""
    target_word_lower = target_word.lower()
    english_lower = english.lower()
    return any(
        word.get('language') == language and 
        (word.get('target_word', '').lower() == target_word_lower or 
         word.get('english', '').lower() == english_lower) 
        for word in existing_words
    )

# Function to add a word to Qdrant, now with language
def add_word(target_word, english, language):
    if language not in SUPPORTED_LANGUAGES:
        st.error(f"Invalid language: {language}. Must be one of {SUPPORTED_LANGUAGES}")
        return False
        
    try:
        # First fetch existing words
        existing_words = fetch_words()
        
        # Check for duplicates for the given language
        if is_duplicate_word(target_word, english, language, existing_words):
            st.error(f"Word already exists for {language}! Either '{target_word}' or '{english}' is already in the database for this language.")
            return False
            
        # Use UUID for potentially better uniqueness than random int
        point_id = str(uuid.uuid4())
        client.upsert(
            collection_name="words",
            wait=True, # Wait for confirmation
            points=[
                models.PointStruct(
                    id=point_id, 
                    payload={
                        "target_word": target_word, # Use generic field name
                        "english": english,
                        "language": language, # Store the language
                        "created_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            ]
        )
        st.success(f"Word ('{target_word}' - '{english}' [{language}]) added successfully!")
        return True
    except Exception as e:
        st.error(f"Error adding word: {e}")
        return False

# Function to update a word in Qdrant
def update_word(id, target_word, english, language): # Language is needed for duplicate check
    if language not in SUPPORTED_LANGUAGES:
         st.error(f"Invalid language: {language}. Must be one of {SUPPORTED_LANGUAGES}")
         return False # Should not happen if fetched correctly, but good sanity check

    try:
        # First fetch existing words
        existing_words = fetch_words()
        
        # Filter out the current word (identified by id) from duplicate check
        other_words = [w for w in existing_words if str(w.get('id', '')) != str(id)]
        
        # Check for duplicates against other words of the same language
        if is_duplicate_word(target_word, english, language, other_words):
            st.error(f"Cannot update: Either '{target_word}' or '{english}' already exists in another entry for {language}.")
            return False
            
        # Fetch the existing point to preserve created_at or other fields if necessary
        # Note: This requires the ID to be correctly passed and exist.
        # Qdrant upsert with the same ID overwrites payload by default.
        # We just need to ensure the payload has all required fields.
        
        client.upsert(
            collection_name="words",
            wait=True,
            points=[
                models.PointStruct(
                    id=id, # Use the existing ID to update
                    payload={
                        "target_word": target_word, # Use generic field name
                        "english": english,
                        "language": language, # Ensure language is preserved/correct
                        # Keep created_at if it exists? Or just add updated_at?
                        # For simplicity, we overwrite with new data + updated_at
                        "updated_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            ]
        )
        st.success(f"Word (ID: {id}) updated successfully!")
        return True
    except Exception as e:
        st.error(f"Error updating word (ID: {id}): {e}")
        return False

# Function to delete a word from Qdrant (remains largely the same, ID is key)
def delete_word(id):
    try:
        client.delete(
            collection_name="words",
            points_selector=models.PointIdsList(
                points=[str(id)] # Ensure ID is string if using UUIDs
            ),
            wait=True
        )
        st.success(f"Word (ID: {id}) deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting word (ID: {id}): {e}")

# Modified to accept language and use target_word
def insert_words_into_db(words, language):
    if language not in SUPPORTED_LANGUAGES:
        st.error(f"Invalid language for import: {language}. Must be one of {SUPPORTED_LANGUAGES}")
        return
        
    try:
        # First fetch existing words
        existing_words = fetch_words()
        points = []
        skipped_words = []
        added_words = []

        # Expecting `words` to be a list of dicts like {'target_word': '...', 'english': '...'}
        for word_data in words:
            target_word = word_data.get('target_word')
            english = word_data.get('english')

            if not target_word or not english:
                st.warning(f"Skipping incomplete word data: {word_data}")
                continue

            # Perform language-specific duplicate check
            if is_duplicate_word(target_word, english, language, existing_words):
                skipped_words.append(f"{target_word} - {english} [{language}]")
                continue

            # Generate a unique ID for each word
            point_id = str(uuid.uuid4())
            points.append(
                models.PointStruct(
                    id=point_id, 
                    payload={
                        "target_word": target_word,
                        "english": english,
                        "language": language, # Assign the language for the batch
                        "created_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            )
            # Add the newly added word to existing_words for subsequent checks within the same batch
            existing_words.append({
                 'id': point_id, 
                 'target_word': target_word, 
                 'english': english, 
                 'language': language
            })
            added_words.append(f"{target_word} - {english} [{language}]")
        
        if points:
            client.upsert(
                collection_name="words",
                points=points,
                wait=True
            )
            st.success(f"Added {len(points)} new words for language '{language}' successfully!")
            if added_words:
                st.write("Added words:", added_words)
        else:
            st.info("No new words were added.")
        
        if skipped_words:
            st.warning(f"Skipped {len(skipped_words)} duplicate words for language '{language}':")
            st.write("Skipped words:", skipped_words)
            
    except Exception as e:
        st.error(f"Error inserting words for language '{language}': {e}")

# --- Data Migration Function ---
def migrate_missing_language():
    st.info("Starting data migration: Adding 'language: salish' to points missing the field...")
    updated_count = 0
    checked_count = 0
    points_to_update = []

    try:
        # Scroll through all points in the collection
        offset = None
        while True:
            scroll_result, next_offset = client.scroll(
                collection_name="words",
                limit=100, # Process in batches
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            checked_count += len(scroll_result)

            for point in scroll_result:
                payload = point.payload
                # Check if payload is a dict and language field is missing
                if isinstance(payload, dict) and 'language' not in payload:
                    points_to_update.append(point.id)
            
            if next_offset is None:
                break # No more pages
            offset = next_offset

        st.info(f"Checked {checked_count} points. Found {len(points_to_update)} points missing the language field.")

        if points_to_update:
            st.info("Applying updates...")
            # Update points in batches if the list is very large, or one by one
            # set_payload can take a list of points and a payload to set for all of them,
            # or update individual points. Let's update individually for clarity.
            for point_id in points_to_update:
                 try:
                     client.set_payload(
                         collection_name="words",
                         payload={"language": "salish"}, # Payload to add/overwrite
                         points=[point_id], # ID of the point to update
                         wait=True
                     )
                     updated_count += 1
                 except Exception as update_err:
                     st.warning(f"Failed to update point {point_id}: {update_err}")
            
            st.success(f"Migration complete. Successfully updated {updated_count} points.")
        else:
            st.success("Migration check complete. No points required updating.")

    except Exception as e:
        st.error(f"Error during migration: {e}")

# Function to generate vocabulary using Amazon Bedrock - ADD LANGUAGE PARAM
def generate_vocabulary(prompt, language):
    if language not in SUPPORTED_LANGUAGES:
        st.error(f"Cannot generate vocabulary for unsupported language: {language}")
        return []
        
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

    # Update prompt to specify language and format
    generation_prompt = f"{prompt} Generate 10 vocabulary words with translations between English and {language.capitalize()}. Format each line strictly as: {language.capitalize()} Word - English Word. Include only the words per line, no numbering, backticks, or other formatting."
    
    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"text": generation_prompt}]
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
        # Pass language to parser and inserter
        words = parse_generated_text(generated_text, language) 
        if words:
            insert_words_into_db(words, language) 
        else:
            st.warning("Could not parse any words from the generated text.")
        return words

    except Exception as e:
        st.error(f"Error calling Bedrock: {e}")
        return []

# Modified parser to handle language and target_word
def parse_generated_text(generated_text, language):
    words = []
    # Clean the text of any backticks
    cleaned_text = generated_text.replace('`', '').strip()
    
    for line in cleaned_text.split('\n'):
        if not line.strip():
            continue
        
        # Clean each line
        clean_line = line.strip()
        parts = clean_line.split(' - ')
        
        if len(parts) == 2:  # Expecting Target Language Word - English Word
            target_word_part = parts[0].strip()
            english_part = parts[1].strip()
            
            if target_word_part and english_part:  # Only add if both parts are non-empty
                words.append({
                    # The key is now generic 'target_word'
                    "target_word": target_word_part, 
                    "english": english_part
                    # Language is handled by the calling function (insert_words_into_db)
                })
        else:
             st.warning(f"Skipping malformed line (expected 'Target - English'): '{line}'")
            
    st.write(f"Parsed {len(words)} words from generated text for language '{language}'.")
    return words

# Streamlit UI
# Use language name in title
st.title(f"Vocabulary Loader (Salish & Italian)")

# Sidebar options
# Add "Data Migration" to the options
operation = st.sidebar.selectbox("Choose an operation", ["Generate", "CRUD", "Import/Export", "Data Migration"])

if operation == "Generate":
    st.header("Generate Vocabulary")
    # Add language selection for generation
    selected_language_gen = st.selectbox("Select Language to Generate", SUPPORTED_LANGUAGES, key="lang_gen")
    
    prompt = st.text_area(f"Enter a prompt for {selected_language_gen.capitalize()} vocabulary generation")
    if st.button("Generate"):
        if prompt and selected_language_gen:
            # Pass selected language to generate function
            generated_words = generate_vocabulary(prompt, selected_language_gen) 
            st.write(f"Generated {selected_language_gen.capitalize()} Words (Attempted Insert):")
            # Display format includes target_word
            if generated_words:
                display_words = [{'Target Word': w['target_word'], 'English': w['english']} for w in generated_words]
                st.table(display_words)
        else:
            st.warning("Please enter a prompt and select a language.")

elif operation == "CRUD":
    st.header("CRUD Operations")
    words = fetch_words() # Fetches all words with language and id

    # Display words in a table with language
    if words:
        st.write("Existing Words:")
        # Prepare data for display, ensuring all keys exist
        display_data = []
        for w in words:
             display_data.append({
                 'ID': w.get('id', 'N/A'), 
                 'Language': w.get('language', 'N/A').capitalize(), 
                 'Target Word': w.get('target_word', 'N/A'), 
                 'English': w.get('english', 'N/A'),
                 'Created At': w.get('created_at', 'N/A')
             })
        st.dataframe(display_data) # Use dataframe for better display/sorting
    else:
        st.info("No words found in the database.")

    # Add word form with language selection
    st.subheader("Add New Word")
    selected_language_add = st.selectbox("Language", SUPPORTED_LANGUAGES, key="lang_add")
    # Use generic label
    new_target_word = st.text_input(f"{selected_language_add.capitalize()} Word", key="target_add") 
    new_english = st.text_input("English", key="eng_add")
    if st.button("Add Word"):
        if new_target_word and new_english and selected_language_add:
            # Pass selected language to add function
            if add_word(new_target_word, new_english, selected_language_add):
                # Refresh the word list after adding
                st.experimental_rerun() # Rerun script to show updated list
        else:
            st.warning("Please fill in all fields and select a language.")

    # Update word form - simplifying: get ID, show current, allow edit
    st.subheader("Update Word")
    if words:
        # Select word by ID might be more robust if list is long
        word_options = {str(w.get('id', '')): f"{w.get('target_word', '')} - {w.get('english', '')} [{w.get('language', '')}]" for w in words if w.get('id')}
        selected_id_str = st.selectbox(
            "Select word to update (by ID)",
            options=list(word_options.keys()),
            format_func=lambda k: word_options[k], 
            key="update_select"
        )
        
        word_to_update = next((w for w in words if str(w.get('id', '')) == selected_id_str), None)

        if word_to_update:
            st.text(f"Selected Language: {word_to_update.get('language', 'N/A').capitalize()}") # Display language
            # Use generic labels, prepopulate with existing values
            update_target_word = st.text_input("New Target Word", value=word_to_update.get('target_word', ''), key="target_update")
            update_english = st.text_input("New English", value=word_to_update.get('english', ''), key="eng_update")
            
            # Get the language from the word being updated for the duplicate check
            update_language = word_to_update.get('language', 'salish') 

            if st.button("Update Word"): # Changed button label
                if update_target_word and update_english and selected_id_str:
                    # Pass the original language for the check
                    if update_word(selected_id_str, update_target_word, update_english, update_language):
                        # Refresh the word list after updating
                        st.experimental_rerun()
                else:
                    st.warning("Please fill in all fields.")
        else:
             st.info("Select a word from the list above to update.")

    # Delete word form - selecting by ID
    st.subheader("Delete Word")
    if words:
        # Use the same selection mechanism as update
        selected_id_del_str = st.selectbox(
            "Select word to delete (by ID)",
            options=list(word_options.keys()),
            format_func=lambda k: word_options[k], 
            key="delete_select"
        )
        
        word_to_delete = next((w for w in words if str(w.get('id', '')) == selected_id_del_str), None)

        if word_to_delete and st.button("Delete Word"): # Changed button label
            delete_word(selected_id_del_str)
            # Refresh the word list after deleting
            st.experimental_rerun()
        elif not word_to_delete:
            st.info("Select a word from the list above to delete.")

elif operation == "Import/Export":
    st.header("Import/Export Vocabulary")

    # Export - Ensure exported data has target_word and language
    st.subheader("Export Vocabulary")
    if st.button("Export to JSON"):
        words_to_export = fetch_words() # Fetch fresh data with language/target_word
        if words_to_export:
            # Prepare for export, maybe remove internal IDs if not needed externally?
            export_data = [{'target_word': w.get('target_word'), 'english': w.get('english'), 'language': w.get('language')} for w in words_to_export]
            json_data = json.dumps(export_data, indent=4, ensure_ascii=False)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="vocabulary_export.json", # Changed filename
                mime="application/json",
            )
        else:
            st.info("No words to export.")

    # Import - Add language selection
    st.subheader("Import Vocabulary")
    selected_language_import = st.selectbox("Select Language for Imported File", SUPPORTED_LANGUAGES, key="lang_import")
    uploaded_file = st.file_uploader(f"Upload a JSON file (for {selected_language_import.capitalize()} language)", type=["json"], key="import_upload")
    
    if uploaded_file is not None and selected_language_import:
        try:
            # Assuming JSON structure is [{ "target_word": "...", "english": "..." }, ...]
            # Or potentially legacy { "salish": "...", "english": "..." }
            raw_data = json.loads(uploaded_file.read().decode("utf-8"))
            
            # Normalize data to { "target_word": "...", "english": "..." }
            words_to_import = []
            for item in raw_data:
                if isinstance(item, dict):
                    english = item.get('english')
                    target = item.get('target_word')
                    # Handle legacy format where 'salish' might be present
                    if not target and selected_language_import == 'salish' and 'salish' in item:
                        target = item.get('salish')
                    # Add more specific checks if Italian files might use 'italian' key
                    elif not target and selected_language_import == 'italian' and 'italian' in item:
                         target = item.get('italian')
                        
                    if target and english:
                        words_to_import.append({'target_word': target, 'english': english})
                    else:
                        st.warning(f"Skipping invalid item during import: {item}")
                else:
                    st.warning(f"Skipping non-dictionary item during import: {item}")

            st.write(f"Previewing {len(words_to_import)} words to import as {selected_language_import.capitalize()}:")
            st.dataframe(words_to_import)

            if st.button("Add Imported Words to Database"):
                # Pass the list of dicts and the selected language
                insert_words_into_db(words_to_import, selected_language_import) 
                st.experimental_rerun()

        except json.JSONDecodeError:
            st.error("Invalid JSON format.")
        except Exception as e:
            st.error(f"Error processing imported file: {e}")

# --- Data Migration UI ---
elif operation == "Data Migration":
    st.header("Database Migration Utilities")
    st.warning("Use these tools carefully. Backup your data if possible before running migrations.")
    
    st.subheader("Add Missing Language Field")
    st.write("This tool checks all entries in the 'words' collection. \n             If an entry does not have a 'language' field in its payload, \n             it will be assigned 'language: salish'. This is useful for updating older data.")
    
    if st.button("Run Salish Language Migration"):
        migrate_missing_language() # Call the migration function
