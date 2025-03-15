import boto3
import json
import re
from config import AWS_REGION, BEDROCK_MODEL_ID, TARGET_LANGUAGE
from utils.aws_utils import bedrock_runtime, invoke_bedrock

def generate_vocabulary(lyrics, target_language=TARGET_LANGUAGE):
    """
    Generates a list of vocabulary words and their definitions from the lyrics,
    now including translations to English.
    
    Args:
        lyrics (str): The lyrics of the song.
        target_language (str, optional): The target language for vocabulary. Defaults to TARGET_LANGUAGE.
        
    Returns:
        list: A list of vocabulary words with definitions, examples, and translations.
    """
    prompt_data = f"""
    Analyze the song lyrics below and identify 5 important vocabulary words that would be helpful for someone learning {target_language}.
    
    For each word, provide:
    1. The word in {target_language}
    2. A definition of the word in {target_language}
    3. An example sentence using the word in {target_language} from the lyrics if possible, otherwise create a simple sentence
    4. The translation of the word in English
    
    IMPORTANT: Your response must be a valid, parseable JSON array containing 5 objects. 
    Use this exact format without any additional text or explanation:
    
    [
      {{
        "word": "example_word",
        "definition": "example definition in {target_language}",
        "example": "example sentence in {target_language}",
        "translation": "English translation"
      }},
      // ... more word objects
    ]
    
    Lyrics:
    {lyrics}
    """
    
    try:
        llm_output = invoke_bedrock(prompt_data)
        
        # Try to extract JSON from the response if it's embedded in other text
        json_match = re.search(r'\[\s*\{.*\}\s*\]', llm_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                json_output = json.loads(json_str)
                if isinstance(json_output, list):
                    vocabulary_list = []
                    for item in json_output:
                        word = item.get("word", "").strip()
                        definition = item.get("definition", "").strip()
                        example = item.get("example", "").strip()
                        translation = item.get("translation", "").strip()
                        if word and definition:
                            vocabulary_list.append({
                                "word": word,
                                "definition": definition,
                                "example": example,
                                "translation": translation
                            })
                    
                    return vocabulary_list[:5]  # Limit to 5 words
            except json.JSONDecodeError:
                print("Could not decode extracted JSON, falling back to regex parsing.")
        else:
            print("No JSON array pattern found in the response, falling back to regex parsing.")
        
        # Regex parsing fallback
        print("Using regex parsing for vocabulary extraction.")
        words = re.findall(r"Word:\s*(.*?)\n|\"word\":\s*\"(.*?)\"", llm_output)
        definitions = re.findall(r"Definition:\s*(.*?)\n|\"definition\":\s*\"(.*?)\"", llm_output)
        examples = re.findall(r"Example:\s*(.*?)\n|\"example\":\s*\"(.*?)\"", llm_output)
        translations = re.findall(r"Translation:\s*(.*?)(?:\n|$)|\"translation\":\s*\"(.*?)\"", llm_output)
        
        vocabulary_list = []
        for i in range(min(len(words), len(definitions), len(examples), len(translations))):
            # For each regex match, we need to handle both capturing groups
            word = next((w for w in words[i] if w), "")
            definition = next((d for d in definitions[i] if d), "")
            example = next((e for e in examples[i] if e), "")
            translation = next((t for t in translations[i] if t), "")
            
            vocabulary_list.append({
                "word": word.strip(),
                "definition": definition.strip(),
                "example": example.strip(),
                "translation": translation.strip()
            })
            
        return vocabulary_list[:5]  # Limit to 5 words

    except Exception as e:
        print(f"Error generating vocabulary: {str(e)}")
        return [{"word": "Error", "definition": "Definition not available", "example": "Example not available", "translation": "Translation not available"}]

# Create an alias for backward compatibility
generate_vocabulary_from_text = generate_vocabulary 