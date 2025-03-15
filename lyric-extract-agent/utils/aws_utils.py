import boto3
import json
from config import AWS_REGION, BEDROCK_MODEL_ID

# Initialize Bedrock runtime client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

def get_bedrock_runtime():
    """
    Returns the Bedrock runtime client.
    """
    return bedrock_runtime

def invoke_bedrock(prompt):
    """
    Invoke AWS Bedrock to generate text
    
    Args:
        prompt (str): The prompt for text generation
        
    Returns:
        str: The generated text
    """
    try:
        # Call Amazon Bedrock
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            body=json.dumps(payload),
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        generated_text = response_body['output']['message']['content'][0]['text']
        
        return generated_text
    except Exception as e:
        print(f"Error invoking Bedrock: {str(e)}")
        return "Error generating response." 