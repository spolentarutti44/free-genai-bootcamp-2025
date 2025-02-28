import cv2
import mediapipe as mp
import torch
import numpy as np
import torch.nn as nn
import time  # Add this import for time measurement

# Import the correct model class name
from modelTraining import SimpleCNN  # Changed from HandGestureNet to SimpleCNN

# Import HandGestureCapture from fingerCapture
from fingerCapture import HandGestureCapture

class HandGestureRecognition:
    def __init__(self, model_path='best_model.pt'):
        self.capture = HandGestureCapture()
        
        # Initialize the model with the correct class
        self.model = SimpleCNN()  # Changed from HandGestureNet to SimpleCNN
        
        # Load the saved model weights
        try:
            checkpoint = torch.load(model_path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f"Model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Initializing with random weights. Performance will be poor.")
        
        self.model.eval()  # Set model to evaluation mode
        
        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
    def predict_gesture(self, landmarks):
        if landmarks is None:
            return None
        
        # DEBUG - print raw landmark data to understand its structure
        print(f"Landmark data shape: {len(landmarks)}")
        print(f"Landmark: {landmarks}")
        
        # Convert landmarks to tensor
        landmarks_tensor = torch.FloatTensor(landmarks)
        
        # Normalize landmarks to range [0,1]
        if torch.min(landmarks_tensor) != torch.max(landmarks_tensor):
            landmarks_tensor = (landmarks_tensor - torch.min(landmarks_tensor)) / (torch.max(landmarks_tensor) - torch.min(landmarks_tensor))
        
        # Pad or truncate to 784 values (28*28)
        if landmarks_tensor.size(0) < 784:
            padding = torch.zeros(784 - landmarks_tensor.size(0))
            landmarks_tensor = torch.cat([landmarks_tensor, padding])
        else:
            landmarks_tensor = landmarks_tensor[:784]
        
        # Reshape to match the expected input
        landmarks_image = landmarks_tensor.reshape(1, 1, 28, 28)
        
        # Get prediction and show all class probabilities for debugging
        with torch.no_grad():
            outputs = self.model(landmarks_image)
            
            # Print raw outputs to see if there's a strong bias toward U
            probs = torch.nn.functional.softmax(outputs, dim=1)
            values, indices = torch.topk(probs, 5)
            print("Top 5 predictions:")
            for i in range(5):
                idx = indices[0, i].item()
                letter = self.letters[idx] if idx < len(self.letters) else "?"
                print(f"{letter}: {values[0, i].item():.4f}")
            
            _, predicted = torch.max(outputs.data, 1)
            return self.letters[predicted.item()]
    
    def run_inference(self):
        cap = cv2.VideoCapture(0)
        
        # For calculating FPS
        prev_frame_time = time.time()
        
        predicted_letter = None
        confidence_counter = 0
        stable_prediction = None
        
        # For debouncing
        last_prediction_time = 0
        debounce_interval = 5.0  # 5 seconds debounce
        ready_for_new_prediction = True  # Flag to track if we're ready for a new prediction
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            frame, landmarks = self.capture.process_frame(frame)
            
            # Calculate current time for debounce
            current_time = time.time()
            
            # Check if debounce period has passed
            if current_time - last_prediction_time >= debounce_interval:
                ready_for_new_prediction = True
            
            # Get prediction only if we're ready and have landmarks
            if landmarks is not None and ready_for_new_prediction:
                letter = self.predict_gesture(landmarks)
                
                # Simple stabilization
                if letter == predicted_letter:
                    confidence_counter += 1
                else:
                    predicted_letter = letter
                    confidence_counter = 0
                
                # Update stable prediction if confidence is high enough
                if confidence_counter > 5:
                    # Record prediction even if it's the same as before
                    stable_prediction = predicted_letter
                    last_prediction_time = current_time  # Reset debounce timer
                    ready_for_new_prediction = False  # Not ready for next prediction until debounce expires
                    print(f"Prediction: {stable_prediction}")
            
            # Calculate FPS
            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            
            # Display information on frame
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if stable_prediction:
                cv2.putText(frame, f'Letter: {stable_prediction}', (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show countdown for next prediction
                time_since_last = current_time - last_prediction_time
                if time_since_last < debounce_interval:
                    time_left = int(debounce_interval - time_since_last)
                    cv2.putText(frame, f'Next prediction in: {time_left}s', (10, 110),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, f'Ready for next prediction', (10, 110),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Hand Gesture Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    recognizer = HandGestureRecognition()
    recognizer.run_inference()

if __name__ == "__main__":
    main() 