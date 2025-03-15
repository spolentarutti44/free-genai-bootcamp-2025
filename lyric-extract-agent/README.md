# Lyric Extract Agent

## Overview

This application helps users learn the Salish language through lyrics extraction and analysis. It provides features for retrieving song lyrics, summarizing them, generating vocabulary, and tracking learning progress.

## Features

- **Request Song/Lyrics:** Enter a song title or phrase to retrieve lyrics.
- **Extract Lyrics:** Extract lyrics from songs.
- **Summarize Lyrics:** Get a concise summary of the lyrics.
- **Generate Vocabulary:** Create vocabulary lists based on the lyrics.
- **Conversation History:** Track your learning progress.

## Technical Stack

- **Backend:** Python, Flask, Langchain, AWS Services (Bedrock, Lambda, Qdrant, S3, Textract, Translate, Comprehend)
- **Frontend:** Streamlit
- **NLP:** Amazon Nova Lite v1 LLM via AWS Bedrock
- **Data Storage:** Qdrant

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up AWS credentials:
   ```bash
   aws configure
   ```

3. Set up Qdrant:
   - For local development, you can run Qdrant in Docker:
     ```bash
     docker run -p 6333:6333 qdrant/qdrant
     ```
   - For production, set up a Qdrant instance and update the configuration.

4. Set environment variables (optional):
   ```bash
   export AWS_REGION=us-east-1
   export BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
   export QDRANT_URL=https://89dd69bf-59f2-4c71-bd64-3dd7c5be0285.us-east-1-0.aws.cloud.qdrant.io
   export TARGET_LANGUAGE=Salish
   ```

5. Run the Flask backend:
   ```bash
   python app.py
   ```

6. Run the Streamlit frontend:
   ```bash
   streamlit run streamlit_app.py
   ```

## API

- **GET /lyrics/{song_title}:** Retrieve lyrics for a specific song.
- **GET /lyrics/search:** Search for lyrics by title or phrase.
- **GET /lyrics/summary:** Summarize the lyrics of a song.
- **GET /lyrics/vocabulary:** Generate vocabulary from the lyrics.
- **GET /lyrics/history:** Retrieve the history of the conversation.

## Project Structure

- `app.py`: Main Flask application
- `streamlit_app.py`: Streamlit frontend
- `agents/`: Agent implementations for different functions
- `tools/`: Tool implementations for specific tasks
- `utils/`: Utility functions
- `config.py`: Configuration settings

## Contributors

- Stephen Polentarutti