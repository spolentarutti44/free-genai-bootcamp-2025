import cv2
import mediapipe as mp
import numpy as np
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
import torch
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Pinecone
api_key = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=api_key)

# Create or connect to an index
index_name = 'hand-gestures'
existing_indexes = pc.list_indexes()
print(f"Existing indexes (before check): {existing_indexes}")  # Debugging line

# Ensure existing_indexes is a list of index names
existing_index_names = [index['name'] for index in existing_indexes]
print(f"Extracted index names: {existing_index_names}")  # Debugging line

if index_name not in existing_index_names:
    print(f"Index '{index_name}' NOT found in existing indexes. Proceeding to create...")  # Debugging line
    pc.create_index(
        name=index_name,
        dimension=384,  # Adjust dimension based on your embedding model
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')  # Adjust region as needed
    )
    print(f"Index '{index_name}' created.")
else:
    print(f"Index '{index_name}' ALREADY EXISTS. Connecting to the existing index.")  # Debugging line

# Get index
index = pc.Index(index_name)

class HandGestureCapture:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        landmarks_array = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # Get first hand
            
            # Draw landmarks
            self.mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS
            )
            
            # Convert landmarks to array
            landmarks_array = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
            
        return frame, landmarks_array

    def save_to_pinecone(self, landmarks, label=None):
        if landmarks is not None:
            # Create unique ID for the gesture
            gesture_id = f"gesture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'label': label if label else 'unlabeled'
            }
            
            # Save to Pinecone
            index.upsert(vectors=[(gesture_id, landmarks.tolist(), metadata)])
            print(f"Saved gesture with ID: {gesture_id}")
            return gesture_id
        return None

def main():
    capture = HandGestureCapture()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame
        frame, landmarks = capture.process_frame(frame)
        
        # Display frame
        cv2.imshow('Hand Gesture Capture', frame)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s') and landmarks is not None:
            # Save gesture when 's' is pressed
            gesture_id = capture.save_to_pinecone(landmarks)
            if gesture_id:
                print(f"Saved gesture with ID: {gesture_id}")
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 