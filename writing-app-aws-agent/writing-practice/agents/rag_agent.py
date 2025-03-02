import boto3
import json
import requests
import sqlite3  # Import sqlite3 for database operations
from config import AWS_REGION, DYNAMODB_TABLE_NAME, TARGET_LANGUAGE

DATABASE_PATH = '../../my-learning-api/language_learning.db'

class RAGAgent:
    def __init__(self):
        # Initialize AWS clients
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.comprehend = boto3.client('comprehend', region_name=AWS_REGION)
        self.translate = boto3.client('translate', region_name=AWS_REGION)
        self.bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        
        # Initialize SQLite connection
        self.sqlite_connection = sqlite3.connect(DATABASE_PATH)
        self.sqlite_cursor = self.sqlite_connection.cursor()
        
        #self.create_dynamodb_table();
        # Initialize DynamoDB tables
        self.word_group_table = self.dynamodb.Table(DYNAMODB_TABLE_NAME)
        self.conversation_log_table = self.dynamodb.Table('conversation_logs')
        
        # Create the conversation logs table if it doesn't exist
        #self.create_conversation_log_table()
    
    def get_word_groups(self):
        """Retrieve list of word groups from SQLite database"""
        try:
            self.sqlite_cursor.execute("SELECT name FROM groups")
            rows = self.sqlite_cursor.fetchall()
            return [row[0] for row in rows]  # Extract group names from the rows
        except Exception as e:
            print(f"Error retrieving word groups: {str(e)}")
            return ["Greetings", "Family", "Colors", "Animals", "Food"]
    
    def get_word_group_info(self, name):
        """Get detailed information about a word group from SQLite"""
        try:
            self.sqlite_cursor.execute("SELECT * FROM groups WHERE name = ?", (name,))
            row = self.sqlite_cursor.fetchone()
            if row:
                return {
                    "name": row[0],
                    "description": f"Words related to {name.lower()} in {TARGET_LANGUAGE}",
                    "words": self._get_sample_words(name)  # You can implement this to fetch words
                }
            else:
                return {}
        except Exception as e:
            print(f"Error retrieving word group info: {str(e)}")
            return {
                "name": name,
                "description": f"Words related to {name.lower()} in {TARGET_LANGUAGE}",
                "words": self._get_sample_words(name)
            }
    
    def generate_sentence(self, name):
        """Generate a simple sentence using words from the group"""
        try:
            # Get word group information
            word_group_info = self.get_word_group_info(name)
            words = word_group_info.get('words', self._get_sample_words(name))
            
            # Generate sentence using Amazon Bedrock
            prompt = f"""Generate a simple sentence in {TARGET_LANGUAGE} language using the following words: {', '.join(words)}. 
            The sentence should be grammatically correct and appropriate for a language learner.
            Also provide an English translation.
            """
            
            response = self._invoke_llm(prompt)
            
            # Log conversation
            self._log_conversation("system", prompt, response)
            
            return response
        except Exception as e:
            print(f"Error generating sentence: {str(e)}")
            return f"Sample {TARGET_LANGUAGE} sentence. (English translation: This is a sample sentence.)"
    
    def check_sentence(self, sentence, name):
        """Check a sentence for grammar and vocabulary usage"""
        try:
            # Get word group information
            word_group_info = self.get_word_group_info(name)
            words = word_group_info.get('words', self._get_sample_words(name))
            
            # Generate feedback using Amazon Bedrock
            prompt = f"""Analyze the following sentence in {TARGET_LANGUAGE} language: "{sentence}"
            
            This sentence was written using words related to {name}. The expected vocabulary includes: {', '.join(words)}.
            
            Please provide feedback on:
            1. Grammar and structure
            2. Vocabulary usage
            3. Suggestions for improvement
            
            Keep your feedback encouraging and constructive.
            """
            
            response = self._invoke_llm(prompt)
            
            # Log conversation
            self._log_conversation("user", sentence, response)
            
            return response
        except Exception as e:
            print(f"Error checking sentence: {str(e)}")
            return "Your sentence looks good! Here are some minor suggestions for improvement..."
    
    def get_practice_words(self, topic):
        """Get a list of practice words for a given topic using LLM"""
        try:
            # Generate a prompt for the LLM
            prompt = f"Generate a list of practice words related to '{topic}' in {TARGET_LANGUAGE}. Provide at least 5 words."
            
            # Invoke the LLM to get practice words
            response = self._invoke_llm(prompt)
            
            # Parse the response to extract the words
            # Assuming the response is a string of words separated by commas
            practice_words = [word.strip() for word in response.split(',')]
            
            return practice_words
        except Exception as e:
            print(f"Error getting practice words: {str(e)}")
            return ["word1", "word2", "word3", "word4", "word5"]  # Fallback sample words
    
    def generate_practice_sentences(self, topic, complexity="simple"):
        """Generate practice sentences based on a topic"""
        try:
            # Generate practice sentences using Amazon Bedrock
            prompt = f"""Generate 1 {complexity} sentences in Salish about {topic} that would be useful for someone learning {TARGET_LANGUAGE}.
            These sentences should be appropriate for translation practice. Do not include the translation just have the sentence.
            """
            
            response = self._invoke_llm(prompt)
            
            # Parse the response into a list of sentences
            sentences = [line.strip() for line in response.split('\n') if line.strip()]
            
            return sentences
        except Exception as e:
            print(f"Error generating practice sentences: {str(e)}")
            return [
                f"This is a {complexity} sentence about {topic}.",
                f"Here is another {complexity} sentence about {topic}.",
                f"Let's practice with this {complexity} sentence about {topic}."
            ]
    
    def _invoke_llm(self, prompt):
        """Invoke Amazon Bedrock to generate text"""
        try:
            model_id = "amazon.nova-lite-v1:0"
            content_type = "application/json"
            accept = "application/json"
            # Call Amazon Bedrock (Amazon Nova Lite)
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ]
            }
            
            response = self.bedrock.invoke_model(
                body=json.dumps(payload),
                modelId=model_id,
                contentType=content_type,
                accept=accept
            )
            
            response_body = json.loads(response.get('body').read())
            generated_text = response_body['output']['message']['content'][0]['text']
            print(generated_text)
            return generated_text
        except Exception as e:
            print(f"Error invoking LLM: {str(e)}")
            return "This is a sample response that would be generated by the language model."
    
    def _log_conversation(self, role, input_text, output_text):
        """Log conversation to DynamoDB"""
        try:
            import uuid
            import time
            
            self.conversation_log_table.put_item(
                Item={
                    'conversation_id': str(uuid.uuid4()),
                    'timestamp': int(time.time()),
                    'role': role,
                    'input': input_text,
                    'output': output_text
                }
            )
        except Exception as e:
            print(f"Error logging conversation: {str(e)}")
    
    def _get_sample_words(self, name):
        """Return sample words for a given group name (for demonstration)"""
        # You can implement this to fetch actual words from the SQLite database
        sample_words = {
            "Greetings": ["hello", "goodbye", "thank you", "please", "welcome"],
            "Family": ["mother", "father", "sister", "brother", "grandmother"],
            "Colors": ["red", "blue", "green", "yellow", "black"],
            "Animals": ["dog", "cat", "horse", "bear", "bird"],
            "Food": ["bread", "water", "fruit", "meat", "vegetable"]
        }
        return sample_words.get(name, ["word1", "word2", "word3", "word4", "word5"])

    def create_dynamodb_table(self):
        try:
            table = self.dynamodb.create_table(
                TableName=DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {
                        'AttributeName': 'name',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'name',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print(f"Table {DYNAMODB_TABLE_NAME} created successfully")
            return table
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            print(f"Table {DYNAMODB_TABLE_NAME} already exists")
            return self.dynamodb.Table(DYNAMODB_TABLE_NAME)

    def create_conversation_log_table(self):
        try:
            table = self.dynamodb.create_table(
                TableName='conversation_logs',
                KeySchema=[
                    {
                        'AttributeName': 'conversation_id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'conversation_id',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print("Table 'conversation_logs' created successfully")
            return table
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            print("Table 'conversation_logs' already exists")
            return self.dynamodb.Table('conversation_logs')

    def close_connection(self):
        """Close the SQLite connection when done"""
        self.sqlite_connection.close()