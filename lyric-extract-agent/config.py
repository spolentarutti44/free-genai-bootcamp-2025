import os

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-lite-v1:0')

# Qdrant Configuration
QDRANT_URL = os.getenv('QDRANT_URL', 'https://89dd69bf-59f2-4c71-bd64-3dd7c5be0285.us-east-1-0.aws.cloud.qdrant.io')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.cxoEv3e35nMIxhtP7RFJ2QYO0_-S6OhBBpFMYX70oGc')

# Application Configuration
TARGET_LANGUAGE = os.getenv('TARGET_LANGUAGE', 'Salish') 