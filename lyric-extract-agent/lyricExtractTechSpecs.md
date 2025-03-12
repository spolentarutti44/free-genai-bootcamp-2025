# Salish Language Learning Assistant

## Overview

This application helps users learn the Salish language through an interactive interface that provides writing assistance, document processing, and practice exercises.

## Features

- **Request Song/Lyrics** User enters a song title or phrase and the agent retrieves the lyrics.
- **Extract Lyrics** The agent extracts the lyrics from the song.
- **Summarize Lyrics** The agent summarizes the lyrics.
- **Generate Vocabulary** The agent generates vocabulary from the lyrics.
- **Conversation History:** Track your learning progress by reviewing past interactions.


## Technical Stack

- **Backend:** Python,Flask, Langchain,AWS Services (Bedrock, Lambda, Qdrant, S3, Textract, Translate, Comprehend)
- **Frontend:** Streamlit
- **NLP:** Amazon Nova Lite v1 LLM via AWS Bedrock
- **Data Storage:** Qdrant

## API
- **Lyric ROUTES:** 
    - **GET /lyrics/{song_title}** - Retrieve lyrics for a specific song.
    - **GET /lyrics/search** - Search for lyrics by title or phrase.
    - **GET /lyrics/summary** - Summarize the lyrics of a song.
    - **GET /lyrics/vocabulary** - Generate vocabulary from the lyrics.
    - **GET /lyrics/history** - Retrieve the history of the conversation.

## Agents
- **Lyirc Agent:** use tools available to find and extract lyrics from a song.
- **Song Agent:** use tools available to find a song based on a title or phrase.
- **Vocabulary Agent:** use tools available to generate vocabulary from the lyrics.
- **History Agent:** use tools available to track and manage the history of the conversation
- **Support Agent:** use tools available to support the other agents.
- **SUPERVISOR Agent:** use tools available to supervise the other agents.
- **QDRANT QUERY Agent:** use tools available to query the Qdrant collection.

## Tools

- **DUCKDUCKGO:** use duckduckgo to search the web for information.
- **YOUTUBE:** use youtube to search for a song.
- **EXTRACT_LYRICS:** use a tool to extract lyrics from a song.
- **SUMMARIZE_LYRICS:** use a tool to summarize the lyrics of a song.
- **GENERATE_VOCABULARY:** use a tool to generate vocabulary from the lyrics.
- **COLLECT_HISTORY:** use a tool to track the history of the conversation by appending to a collection in Qdrant via the api.
- **QDRANT_QUERY:** use a tool to query the Qdrant collection.

## Project Structure

- `app.py`: Main Streamlit application
- `agents/`: Contains the Document Processing Agent and RAG Agent
- `utils/`: Utility functions for database operations
- `config.py`: Configuration settings
- `requirements.txt`: List of dependencies
- `lyricExtractTechSpecs.md`: Technical specifications for the project

## Contributors

- Your Name 