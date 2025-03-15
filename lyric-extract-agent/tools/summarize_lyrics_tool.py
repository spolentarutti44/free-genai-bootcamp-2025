import boto3
import json
from config import AWS_REGION, BEDROCK_MODEL_ID

def summarize_lyrics(lyrics):
    """
    Summarize the lyrics of a song using AWS Bedrock
    
    Args:
        lyrics (str): The lyrics to summarize
        
    Returns:
        str: A summary of the lyrics
    """
    # Initialize the Bedrock client
    bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)
    
    # Prepare the prompt for summarization
    prompt = f"""Please provide a concise summary of the following song lyrics:

{lyrics}

The summary should capture the main themes, emotions, and narrative of the song in a few sentences.
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
        
        response = bedrock.invoke_model(
            body=json.dumps(payload),
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        generated_text = response_body['output']['message']['content'][0]['text']
        
        return generated_text
    except Exception as e:
        print(f"Error summarizing lyrics: {str(e)}")
        return "Could not generate summary due to an error. Please try again later." 