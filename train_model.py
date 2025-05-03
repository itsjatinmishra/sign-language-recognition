import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import matplotlib.pyplot as plt

# Ensure model directory exists
model_dir = "model"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Dataset path
dataset_path = "dataset/"

# Image Data Generator for Data Augmentation
datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    validation_split=0.2  # 20% data for validation
)

# Load Training Data
train_data = datagen.flow_from_directory(
    dataset_path + "train",
    target_size=(64, 64),
    color_mode="grayscale",
    batch_size=32,
    class_mode="categorical",
    subset="training"
)

# Load Validation Data
val_data = datagen.flow_from_directory(
    dataset_path + "train",
    target_size=(64, 64),
    color_mode="grayscale",
    batch_size=32,
    class_mode="categorical",
    subset="validation"
)

# Get number of classes dynamically
num_classes = len(train_data.class_indices)

# Model Architecture (CNN)
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(64,64,1)),
    MaxPooling2D(2,2),
    
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')  # Auto-detect number of classes
])

# Compile the Model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the Model
history = model.fit(train_data, validation_data=val_data, epochs=10)

# Save the Model
model.save(os.path.join(model_dir, "asl_model.h5"))
print("✅ Model saved successfully in 'model/asl_model.h5'")

# Plot Training Accuracy & Loss
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Training vs Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Training vs Validation Loss')

plt.show()