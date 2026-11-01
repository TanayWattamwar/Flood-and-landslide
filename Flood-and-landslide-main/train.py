import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Load the dataset
# Replace 'your_dataset.csv' with the path to your actual dataset file.
data = pd.read_csv('dataset.csv')

# Features and target variable
features = [
    'MonsoonIntensity', 'TopographyDrainage', 'RiverManagement', 'Deforestation', 
    'Urbanization', 'ClimateChange', 'DamsQuality', 'Siltation', 'AgriculturalPractices', 
    'Encroachments', 'IneffectiveDisasterPreparedness', 'DrainageSystems', 
    'CoastalVulnerability', 'Landslides', 'Watersheds', 'DeterioratingInfrastructure', 
    'PopulationScore', 'WetlandLoss', 'InadequatePlanning', 'PoliticalFactors'
]
target = 'FloodPrediction'  # Replace with your actual target column name

# Splitting the data into features and target
X = data[features]
y = data[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Reshape data for RNN input (samples, time steps, features)
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

# Building the RNN model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1, activation='sigmoid'))  # Use 'sigmoid' for binary classification

# Compiling the RNN
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Training the RNN
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

# Save the model and scaler
model.save('flood_prediction_rnn_model.h5')  # Save the model as HDF5
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Create a pickle file to store the model path and scaler
model_info = {
    'model_path': 'flood_prediction_rnn_model.h5',
    'scaler_path': 'scaler.pkl'
}

with open('model_info.pkl', 'wb') as f:
    pickle.dump(model_info, f)

print("Model and scaler have been saved.")

# To load the saved model and scaler later
# Load the model and scaler paths
with open('model_info.pkl', 'rb') as f:
    model_info = pickle.load(f)

# Load the scaler
with open(model_info['scaler_path'], 'rb') as f:
    loaded_scaler = pickle.load(f)

# Load the trained model
loaded_model = load_model(model_info['model_path'])

# Prediction with loaded model
X_test = loaded_scaler.transform(X_test.reshape(X_test.shape[0], X_test.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))
y_pred = (loaded_model.predict(X_test) > 0.5).astype("int32")

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print(f'Accuracy: {accuracy}')
print('Classification Report:')
print(report)
print('Confusion Matrix:')
print(conf_matrix)
