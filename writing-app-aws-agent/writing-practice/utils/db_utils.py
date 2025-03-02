import boto3
import sqlite3
from config import AWS_REGION, DYNAMODB_TABLE_NAME

def init_dynamodb():
    """Initialize DynamoDB tables if they don't exist"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    
    # Check if word groups table exists
    existing_tables = [table.name for table in dynamodb.tables.all()]
    
    if DYNAMODB_TABLE_NAME not in existing_tables:
        # Create word groups table
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'group_name',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'group_name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=DYNAMODB_TABLE_NAME)
        print(f"Created table {DYNAMODB_TABLE_NAME}")
    
    # Check if conversation logs table exists
    if 'conversation_logs' not in existing_tables:
        # Create conversation logs table
        table = dynamodb.create_table(
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
        
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName='conversation_logs')
        print("Created table conversation_logs")

def import_from_sqlite(sqlite_path, dynamodb_table_name):
    """Import word groups from SQLite database to DynamoDB"""
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Query word groups
        cursor.execute("SELECT * FROM word_group")
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(dynamodb_table_name)
        
        # Import each row to DynamoDB
        for row in rows:
            item = {column_names[i]: row[i] for i in range(len(column_names))}
            table.put_item(Item=item)
        
        conn.close()
        print(f"Imported {len(rows)} word groups to DynamoDB")
        
    except Exception as e:
        print(f"Error importing from SQLite: {str(e)}") 