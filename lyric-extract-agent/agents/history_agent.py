import time
import uuid
from tools.collect_history_tool import save_to_history
from tools.qdrant_query_tool import query_history
from config import TARGET_LANGUAGE

class HistoryAgent:
    def __init__(self):
        pass
    
    def log_interaction(self, action, input_data, output_data):
        """
        Log an interaction to the history
        
        Args:
            action (str): The type of action performed
            input_data (str): The input data for the action
            output_data (any): The output data from the action
        """
        interaction = {
            "id": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "action": action,
            "input": input_data,
            "output": str(output_data),
            "language": TARGET_LANGUAGE
        }
        
        save_to_history(interaction)
    
    def get_history(self, limit=20):
        """
        Retrieve the conversation history
        
        Args:
            limit (int): Maximum number of entries to retrieve
            
        Returns:
            list: The conversation history entries
        """
        return query_history(limit=limit) 