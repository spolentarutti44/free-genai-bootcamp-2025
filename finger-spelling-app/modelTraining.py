# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import numpy as np
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from torchvision import transforms
import matplotlib.pyplot as plt
import os
from torchvision.transforms import ToPILImage
import random

# Set the paths to the training and validation files
#train_file_path = "data/sign_mnist_train/sign_mnist_train.csv"  # Adjust this path as needed
#val_file_path = "data/sign_mnist_test/sign_mnist_test.csv"    # Adjust this path as needed
train_file_path = "data/slp-training/model_training.csv"  # Adjust this path as needed
val_file_path = "data/slp-training/model_validation.csv"    # Adjust this path as needed

# Check if files exist
if not os.path.exists(train_file_path):
    raise FileNotFoundError(f"Please download the Sign Language MNIST training dataset and save it to {train_file_path}")
if not os.path.exists(val_file_path):
    raise FileNotFoundError(f"Please download the Sign Language MNIST validation dataset and save it to {val_file_path}")

# Load the datasets from local files
train_df = pd.read_csv(train_file_path)
val_df = pd.read_csv(val_file_path)

print("First 5 records of training set:", train_df.head())
print("First 5 records of validation set:", val_df.head())

# Preprocess the dataset
class SignLanguageDataset(Dataset):
    def __init__(self, dataframe, transform=None):
        self.dataframe = dataframe
        self.transform = transform
        self.to_pil = ToPILImage()  # Create a transform to convert tensor to PIL Image
        
        # Create a mapping from letters to indices
        self.label_mapping = {letter: idx for idx, letter in enumerate(sorted(dataframe['label'].unique()))}
        
        #Todo: reduce the z index and dimentions being captured in landmark

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        label = row['label']
        
        # Convert label to numerical index
        label_index = self.label_mapping[label]
        
        landmarks = row.drop('label').values.astype('float32')
    
        # Clean up invalid values
        landmarks = np.nan_to_num(landmarks, nan=0.0)
        
        # Normalize to [0,1] range properly (only if values aren't already normalized)
        if np.max(landmarks) > 1.0 or np.min(landmarks) < 0.0:
            min_val = np.min(landmarks)
            max_val = np.max(landmarks)
            # Avoid division by zero with small epsilon
            landmarks = (landmarks - min_val) / (max_val - min_val + 1e-8)
        
        # Apply augmentations
        landmarks = self.augment_landmarks(landmarks)
        
        # Convert to tensor
        landmarks_tensor = torch.FloatTensor(landmarks)
        
        # Pad or resize to match the expected input size for the model
        if landmarks_tensor.size(0) < 784:
            # Pad with zeros if less than 784
            padding = torch.zeros(784 - landmarks_tensor.size(0))
            landmarks_tensor = torch.cat([landmarks_tensor, padding])
        else:
            # Truncate if more than 784
            landmarks_tensor = landmarks_tensor[:784]
        
        # Reshape to match the expected input for the model
        landmarks_tensor = landmarks_tensor.view(1, 1, 28, 28)  # Reshape to [1, 1, 28, 28]
        
        if self.transform:
            # Convert landmarks_tensor to PIL Image before applying transformations
            landmarks_image = self.to_pil(landmarks_tensor.squeeze(0))  # Remove the batch dimension for PIL conversion
            landmarks_tensor = self.transform(landmarks_image)
        
        return landmarks_tensor, label_index  # Return the numerical label index

    def augment_landmarks(self, landmarks):
        # Random rotation
        angle = random.uniform(-10, 10)  # Rotate between -10 and 10 degrees
        rotation_matrix = np.array([[np.cos(np.radians(angle)), -np.sin(np.radians(angle))],
                                     [np.sin(np.radians(angle)), np.cos(np.radians(angle))]])
        
        # Apply rotation to x, y coordinates
        for i in range(0, len(landmarks), 3):  # Iterate over x, y pairs
            x, y = landmarks[i], landmarks[i + 1]
            rotated = rotation_matrix @ np.array([x, y])
            landmarks[i], landmarks[i + 1] = rotated[0], rotated[1]
        
        # Random scaling
        scale = random.uniform(0.9, 1.1)  # Scale between 90% and 110%
        landmarks[::3] *= scale  # Scale x coordinates
        landmarks[1::3] *= scale  # Scale y coordinates
        
        # Random translation
        translation_x = random.uniform(-0.1, 0.1)  # Translate x by -10% to 10%
        translation_y = random.uniform(-0.1, 0.1)  # Translate y by -10% to 10%
        landmarks[::3] += translation_x  # Translate x coordinates
        landmarks[1::3] += translation_y  # Translate y coordinates
        
        return landmarks

# Define transformations
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# Create datasets - directly use the loaded dataframes instead of splitting
train_dataset = SignLanguageDataset(train_df, transform=transform)
val_dataset = SignLanguageDataset(val_df, transform=transform)

# Create data loaders
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

# Define a simple model
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(32) # Batch Norm after conv1
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(64) # Batch Norm after conv2
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.dropout1 = nn.Dropout(0.5) # Dropout before fc2
        self.fc2 = nn.Linear(128, 25)

    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x))) # BN before ReLU, common practice
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.bn2(self.conv2(x))) # BN before ReLU
        x = torch.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout1(x) # Apply dropout
        x = self.fc2(x)
        return x

# Initialize the model, loss function, and optimizer
model = SimpleCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# Training loop
def train_model(num_epochs=10):
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for landmarks_tensor, labels in train_loader:
            optimizer.zero_grad()
            
            # Convert labels to tensor if needed, then to long type
            if not isinstance(labels, torch.Tensor):
                labels = torch.tensor(labels)
            
            labels = labels.long()  # Convert to long type
            outputs = model(landmarks_tensor)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        # Calculate average training loss
        avg_train_loss = running_loss / len(train_loader)
        train_losses.append(avg_train_loss)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for landmarks_tensor, labels in val_loader:
                if isinstance(labels, torch.Tensor):
                    labels = labels.long()  # Convert labels to LongTensor if they are not already
                else:
                    raise TypeError(f"Expected labels to be a tensor, got {type(labels)}")
                
                outputs = model(landmarks_tensor)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
        avg_val_loss = val_loss / len(val_loader)
        val_losses.append(avg_val_loss)
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
        
        # Save the model if validation loss improves
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), 'best_model.pth')
    
    return train_losses, val_losses

def plot_training_history(train_losses, val_losses):
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training History')
    plt.legend()
    plt.savefig('training_history.png')
    plt.close()

def main():
    # Train the model
    train_losses, val_losses = train_model(num_epochs=200)
    
    # Save the final model regardless of performance
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_losses': train_losses,
        'val_losses': val_losses,
    }, 'final_model.pt')
    print("Training complete. Final model saved.")
    
    # Plot training history
    plot_training_history(train_losses, val_losses)

if __name__ == "__main__":
    main() 