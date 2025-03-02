import os

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'word_groups')

# Application Configuration
TARGET_LANGUAGE = os.getenv('TARGET_LANGUAGE', 'Salish')
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', '../my-learning-api/learning_portal.db')

# LLM Configuration
LLM_MODEL_ID = os.getenv('LLM_MODEL_ID', 'amazon.nova-lite-v1') 