# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
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

# Set the paths to the training and validation files
#train_file_path = "data/sign_mnist_train/sign_mnist_train.csv"  # Adjust this path as needed
#val_file_path = "data/sign_mnist_test/sign_mnist_test.csv"    # Adjust this path as needed
train_file_path = "data/slp-training/model_tranining.csv"  # Adjust this path as needed
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

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        label = row['label']
        image = row.drop('label').values.astype('float32').reshape(28, 28)  # Assuming 28x28 images
        if self.transform:
            image = self.transform(image)
        return image, label

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
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 25)  # Assuming 25 classes for sign language

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Initialize the model, loss function, and optimizer
model = SimpleCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.00001)

# Training loop
def train_model(num_epochs=10):
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        # Calculate average training loss
        avg_train_loss = running_loss/len(train_loader)
        train_losses.append(avg_train_loss)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
        avg_val_loss = val_loss/len(val_loader)
        val_losses.append(avg_val_loss)
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
        
        # Save the model if validation loss improves
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            # Save both the model architecture and weights
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss,
            }, 'best_model.pt')
            print(f"Model saved at epoch {epoch+1} with validation loss: {avg_val_loss:.4f}")
    
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
    train_losses, val_losses = train_model(num_epochs=50)
    
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