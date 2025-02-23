import boto3
import json

def test_bedrock_connection():
    try:
        # Create a Bedrock Runtime client
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'  # Make sure this matches your configured region
        )
        
        # Test parameters for Claude
        body = json.dumps({
            "prompt": "Hello! How are you?",
            "max_tokens_to_sample": 100,
            "temperature": 0.7,
        })
        
        # Make a test request
        response = bedrock.invoke_model(
            modelId="amazon.nova-lite-v1:0",  # or another model ID you want to use
            body=body
        )
        
        # Parse and print the response
        response_body = json.loads(response['body'].read())
        print("Bedrock Connection Test Successful!")
        print("Response:", response_body['completion'])
        
    except Exception as e:
        print("Error testing Bedrock connection:", str(e))

# Run the test
if __name__ == "__main__":
    test_bedrock_connection()