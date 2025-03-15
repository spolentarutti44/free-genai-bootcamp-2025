import os

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-lite-v1:0')

# Qdrant Configuration
QDRANT_URL = os.getenv('QDRANT_URL', '')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', '')

# Application Configuration
TARGET_LANGUAGE = os.getenv('TARGET_LANGUAGE', 'Salish') 