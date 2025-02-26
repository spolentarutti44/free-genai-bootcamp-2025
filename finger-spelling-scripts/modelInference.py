import cv2
import mediapipe as mp
import torch
import numpy as np
from fingerCapture import HandGestureCapture
from modelTraining import HandGestureNet

class HandGestureRecognition:
    def __init__(self, model_path='best_model.pth'):
        self.capture = HandGestureCapture()
        self.model = HandGestureNet()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
    def predict_gesture(self, landmarks):
        if landmarks is None:
            return None
        
        # Convert landmarks to tensor
        input_tensor = torch.FloatTensor(landmarks).unsqueeze(0)
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            _, predicted = torch.max(outputs.data, 1)
            return self.letters[predicted.item()]
    
    def run_inference(self):
        cap = cv2.VideoCapture(0)
        
        # For calculating FPS
        prev_frame_time = 0
        new_frame_time = 0
        
        predicted_letter = None
        confidence_counter = 0
        stable_prediction = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            frame, landmarks = self.capture.process_frame(frame)
            
            # Get prediction
            if landmarks is not None:
                letter = self.predict_gesture(landmarks)
                
                # Simple stabilization
                if letter == predicted_letter:
                    confidence_counter += 1
                else:
                    predicted_letter = letter
                    confidence_counter = 0
                
                # Update stable prediction if confidence is high enough
                if confidence_counter > 5:
                    stable_prediction = predicted_letter
            
            # Calculate FPS
            new_frame_time = cv2.getTime()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            
            # Display information on frame
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if stable_prediction:
                cv2.putText(frame, f'Letter: {stable_prediction}', (10, 70),
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