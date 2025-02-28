import cv2
import mediapipe as mp
import csv
import os

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
            landmarks_array = [lm.x for lm in hand_landmarks.landmark] + \
                              [lm.y for lm in hand_landmarks.landmark] + \
                              [lm.z for lm in hand_landmarks.landmark]
            
        return frame, landmarks_array

def main():
    capture = HandGestureCapture()
    cap = cv2.VideoCapture(0)
    
    # Ensure the CSV file exists
    csv_file = 'data/slp-training/model_validation.csv'
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)  # Create directory if it doesn't exist
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['label'] + [f'landmark_{i}' for i in range(63 * 3)])  # 63 landmarks with x, y, z

    while True:
        # Prompt user for input
        user_input = input("Enter the letter you are signing and press Enter (or type 'exit' to quit): ").strip().upper()
        if user_input == 'EXIT':
            break
        
        print("Press the spacebar to capture the gesture...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image. Please try again.")
                continue
            
            # Display frame
            cv2.imshow('Hand Gesture Capture', frame)
            
            # Wait for the user to press the spacebar
            if cv2.waitKey(1) & 0xFF == ord(' '):
                # Process frame
                frame, landmarks = capture.process_frame(frame)
                
                if landmarks is not None:
                    # Append landmarks to CSV file
                    with open(csv_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([user_input] + landmarks)
                    print(f"Gesture for '{user_input}' saved.")
                else:
                    print("No hand detected. Please try again.")
                
                break  # Exit the inner loop to prompt for the next letter
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 