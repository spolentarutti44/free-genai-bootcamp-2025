# Salish Language Learning Assistant

## Overview

This application helps users learn the Salish language through an interactive interface that provides writing assistance, document processing, and practice exercises.

## Features

- **Document Writing Group:** Select a word group and generate example sentences to help with writing in Salish.
- **Document Processing:** Upload handwritten sentences for analysis and feedback.
- **Practice Area:** Practice vocabulary and sentence construction at different complexity levels.
- **Conversation History:** Track your learning progress by reviewing past interactions.

## Technical Stack

- **Backend:** Python, AWS Services (Bedrock, Lambda, DynamoDB, S3, Textract, Translate, Comprehend)
- **Frontend:** Streamlit
- **NLP:** Amazon Nova Lite v1 LLM via AWS Bedrock
- **Data Storage:** AWS DynamoDB

## Setup

## Commit a338e2f9f39d5c273a02a5186e6c71f754828c8e associated with this project

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up AWS credentials:
   ```bash
   aws configure
   ```

3. Set environment variables (optional):
   ```bash
   export AWS_REGION=us-east-1
   export DYNAMODB_TABLE_NAME=word_groups
   export TARGET_LANGUAGE=Salish
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Navigate to the "Document Writing Group" page
2. Select a word group from the dropdown menu
3. Generate an example sentence based on the selected word group
4. Write your own sentence in Salish
5. Submit your sentence for feedback or upload a handwritten document

## Project Structure

- `app.py`: Main Streamlit application
- `agents/`: Contains the Document Processing Agent and RAG Agent
- `utils/`: Utility functions for database operations
- `config.py`: Configuration settings

## Contributors

- Your Name 