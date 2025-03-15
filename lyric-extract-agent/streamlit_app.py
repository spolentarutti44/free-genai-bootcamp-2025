import streamlit as st
import requests
import json
from config import TARGET_LANGUAGE

# Configure the API endpoint
API_BASE_URL = "http://localhost:5001"

st.title("Salish Language Learning Assistant - Lyric Extractor")
st.sidebar.title("Navigation")

# Navigation
page = st.sidebar.radio("Go to", ["Search Songs", "View Lyrics", "Summarize Lyrics", "Generate Vocabulary", "Chat with Agent", "History"])

# Helper function to safely parse JSON responses
def safe_json_parse(response):
    try:
        return response.json()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON. Status code: {response.status_code}, Content: {response.text}")
        return {"error": "Failed to decode response from server"}

if page == "Search Songs":
    st.header("Search for Songs")
    
    query = st.text_input("Enter a song title or phrase:")
    
    if st.button("Search"):
        if query:
            try:
                with st.spinner("Searching for songs..."):
                    response = requests.get(f"{API_BASE_URL}/lyrics/search", params={"query": query})
                    
                    if response.status_code == 200:
                        data = safe_json_parse(response)
                        results = data.get("results", [])
                        if results:
                            st.success(f"Found {len(results)} results")
                            for i, result in enumerate(results, 1):
                                st.write(f"{i}. {result['title']} - {result['artist']}")
                        else:
                            st.warning("No results found")
                    else:
                        st.error(f"Error: {safe_json_parse(response).get('error', f'Server returned status code {response.status_code}')}")
            except requests.RequestException as e:
                st.error(f"Connection error: {str(e)}. Make sure the API server is running at {API_BASE_URL}")
        else:
            st.warning("Please enter a search query")

elif page == "View Lyrics":
    st.header("View Song Lyrics")
    
    song_title = st.text_input("Enter the song title:")
    
    if st.button("Get Lyrics"):
        if song_title:
            with st.spinner("Fetching lyrics..."):
                response = requests.get(f"{API_BASE_URL}/lyrics/{song_title}")
                
                if response.status_code == 200:
                    lyrics = response.json().get("lyrics", "")
                    st.subheader(f"Lyrics for {song_title}")
                    st.write(lyrics)
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        else:
            st.warning("Please enter a song title")

elif page == "Summarize Lyrics":
    st.header("Summarize Song Lyrics")
    
    song_title = st.text_input("Enter the song title:")
    
    if st.button("Summarize"):
        if song_title:
            with st.spinner("Summarizing lyrics..."):
                response = requests.get(f"{API_BASE_URL}/lyrics/summary", params={"song_title": song_title})
                
                if response.status_code == 200:
                    summary = response.json().get("summary", "")
                    st.subheader(f"Summary for {song_title}")
                    st.write(summary)
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        else:
            st.warning("Please enter a song title")

elif page == "Generate Vocabulary":
    st.header(f"Generate Vocabulary from Lyrics ({TARGET_LANGUAGE})")
    
    song_title = st.text_input("Enter the song title:")
    
    if st.button("Generate Vocabulary"):
        if song_title:
            with st.spinner(f"Generating vocabulary in {TARGET_LANGUAGE}..."):
                response = requests.get(f"{API_BASE_URL}/lyrics/vocabulary", params={"song_title": song_title})
                
                if response.status_code == 200:
                    try:
                        data = safe_json_parse(response)
                        vocabulary = data.get("vocabulary", [])
                        
                        if vocabulary:
                            st.success(f"Generated vocabulary for {song_title} in {TARGET_LANGUAGE}")
                            for i, word_info in enumerate(vocabulary, 1):
                                target_word = word_info.get('word', 'Unknown word')
                                with st.expander(f"{i}. {target_word} ({TARGET_LANGUAGE})"):
                                    st.write(f"**Definition ({TARGET_LANGUAGE}):** {word_info.get('definition', 'Definition not available')}")
                                    
                                    example = word_info.get('example', '')
                                    if example:
                                        st.write(f"**Example ({TARGET_LANGUAGE}):** {example}")
                                    
                                    translation = word_info.get('translation', '')
                                    if translation:
                                        st.write(f"**Translation (English):** {translation}")
                        else:
                            st.warning("No vocabulary items found")
                    except Exception as e:
                        st.error(f"Error processing vocabulary data: {str(e)}")
                else:
                    st.error(f"Error: {safe_json_parse(response).get('error', f'Server returned status code {response.status_code}')}")
        else:
            st.warning("Please enter a song title")

elif page == "Chat with Agent":
    st.header("Chat with Lyric Assistant")
    
    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user input
    if prompt := st.chat_input("Ask about lyrics, songs, or vocabulary..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    response = requests.post(
                        f"{API_BASE_URL}/ask",
                        json={"query": prompt},
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        response_data = safe_json_parse(response)
                        if response_data.get("success", False):
                            message = response_data.get("response", "I couldn't process that. Please try again.")
                            st.markdown(message)
                            
                            # Add assistant message to chat history
                            st.session_state.messages.append({"role": "assistant", "content": message})
                        else:
                            error_msg = response_data.get("response", "Unknown error")
                            st.error(f"Error: {error_msg}")
                            st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
                    else:
                        error_msg = f"Server returned status code {response.status_code}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.RequestException as e:
                error_msg = f"Connection error: {str(e)}. Make sure the API server is running at {API_BASE_URL}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

elif page == "History":
    st.header("Conversation History")
    
    if st.button("Load History"):
        with st.spinner("Loading history..."):
            response = requests.get(f"{API_BASE_URL}/lyrics/history")
            
            if response.status_code == 200:
                history = response.json().get("history", [])
                
                if history:
                    for i, entry in enumerate(history, 1):
                        with st.expander(f"{i}. {entry['action']} - {entry['timestamp']}"):
                            st.write(f"**Input:** {entry['input']}")
                            st.write(f"**Output:** {entry['output']}")
                else:
                    st.info("No history found")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This app helps extract and learn from song lyrics to enhance language learning."
) 