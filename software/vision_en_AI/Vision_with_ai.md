# Vision with AI

In this markdown file we will experiment with AI for vision applications. We will use the pytorch framework.
PyTorch is an open-source machine learning library developed by Facebook's AI Research lab. It is widely used for applications such as natural language processing and computer vision. PyTorch provides a multi-dimensional array called Tensor, which is similar to NumPy arrays but can run on GPUs. Tensors are the core data structure used in PyTorch for performing numerical computations.

Let's install it (in the same container as the opencv library):

```bash
apt-get update && apt-get install -y python3 python3-pip

pip install --break-system-packages torch
pip install --break-system-packages torchvision
pip install --break-system-packages torchsummary
pip install --break-system-packages scikit-learn
```

copy the following program to test.py and run it with `python3 test.py`.

```python
import torch

# Check if PyTorch is installed
print(f"PyTorch version: {torch.__version__}")

# Create two tensors and add them
a = torch.tensor([2.0, 3.0])
b = torch.tensor([4.0, 1.0])
c = a + b

print(f"Tensor a: {a}")
print(f"Tensor b: {b}")
print(f"Sum: {c}")

# Check if CUDA is available
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
```

Let's get down to business.  
Run the following code (make sure you have the x server running):

```python
import torch
import torchvision
from torchsummary import summary
import numpy as np
import cv2
from sklearn.metrics import confusion_matrix

# Define a simple CNN
class SimpleCNN(torch.nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(in_channels=1, out_channels=8, kernel_size=3, padding=1)
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = torch.nn.Linear(8 * 14 * 14, 10)  # Flattened size for MNIST

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = x.view(-1, 8 * 14 * 14)  # Flatten
        x = self.fc1(x)
        return x

print ('----------------------------------------------------------------------------------------------')
print (' We gebruiken de dataset van MNIST. Google op MNIST, en kijk bij pictures.')
print (' Loading dataset.....')

# Load MNIST dataset
transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor(), torchvision.transforms.Normalize((0.5,), (0.5,))])
trainset = torchvision.datasets.MNIST(root="./data", train=True, download=True, transform=transform)
testset = torchvision.datasets.MNIST(root="./data", train=False, download=True, transform=transform)

print (' De trainset is opgebouwd uit:')
print (trainset)
print (' De testset is opgebouwd uit:')
print (testset)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=256, shuffle=True)
testloader = torch.utils.data.DataLoader(testset, batch_size=1000, shuffle=False)  # Large batch for confusion matrix

print ('----------------------------------------------------------------------------------------------')
print (' De trainset bestaat uit ',len(trainloader),' batches van 256 cijfers')
print (' De testset bestaat uit ',len(testloader),' batches van 1000 cijfers')

# Initialize model, loss, and optimizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleCNN().to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

print ('----------------------------------------------------------------------------------------------')
print (' Het model: ')
summary(model, input_size=(1, 28, 28))
print ('----------------------------------------------------------------------------------------------')
print (' Of simpeler geprint: ')
print (model)

# Train for 20 epochs
print ('----------------------------------------------------------------------------------------------')
print(" Starten met de training...")

train_loss=[]
test_loss=[]
for epoch in range(20):
    trainloss=0.0
    model.train()  # Set model to training mode
    for images, labels in trainloader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        trainloss += loss.item() * images.size(0) 
    # Print the loss on the training set
    trainloss /= len(trainloader.dataset)
    print(f"Epoch [{epoch+1}/20] Training Loss: {trainloss:.4f}")   
    train_loss.append(trainloss)
    
    # Validate the model on the test set
    model.eval()  # Set model to evaluation mode
    testloss = 0.0
    with torch.no_grad():
        for images, labels in testloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            testloss += loss.item() * images.size(0)  # Accumulate test loss
 
    # Compute the average test loss
    testloss /= len(testloader.dataset)
    print(f"Epoch [{epoch+1}/20] Test Loss: {testloss:.4f}")
    test_loss.append(testloss)

print(" Training compleet.")
print ('train loss : ',train_loss)
print ('test loss : ',test_loss)


# Test the trained model and compute confusion matrix
model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for images, labels in testloader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# Compute confusion matrix
conf_matrix = confusion_matrix(all_labels, all_preds)

print ('----------------------------------------------------------------------------------------------')
print(" De Confusion Matrix:\n", conf_matrix)

# Calculate accuracy
# Sum the diagonal elements (correctly classified instances)
correct_predictions = np.sum(np.diag(conf_matrix))
# Total number of instances
total_instances = np.sum(conf_matrix)
# Accuracy calculation
accuracy = correct_predictions / total_instances
print (' De accuracy :',accuracy)

def imshow(text_img, img):
    img = img.squeeze().cpu().numpy()  # Remove the batch dimension and convert to numpy
    img = (img * 255).astype(np.uint8)  # Rescale to 0-255
    cv2.imshow(text_img, img)
    cv2.waitKey(0)  
    cv2.destroyAllWindows() 

# Test the trained model and compute confusion matrix
model.eval()
all_preds = []
all_labels = []
test_images, test_labels = next(iter(testloader))  # Take a batch from testloader

with torch.no_grad():
    outputs = model(test_images.to(device))
    _, predicted = torch.max(outputs, 1)

print ('----------------------------------------------------------------------------------------------')
print (' De foute voorspellingen ')
# Display wrong predictions
for i in range(300):
    if predicted[i] != test_labels[i]:  # If prediction is wrong
        print(f'Image {i} - True Label: {test_labels[i].item()}, Predicted: {predicted[i].item()}')
        imshow(f'Image {i} - True Label: {test_labels[i].item()}, Predicted: {predicted[i].item()}      ', test_images[i]) 
```