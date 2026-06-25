import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load dataset

df = pd.read_csv("student-mat.csv", sep=";")

# Create risk labels

def risk_label(g3):
    if g3 >= 15:
        return 0  # Low Risk
    elif g3 >= 10:
        return 1  # Medium Risk
    else:
        return 2  # High Risk

df["Risk"] = df["G3"].apply(risk_label)

# Features

X = df[
    [
        "G1",
        "G2",
        "absences",
        "studytime",
        "failures"
    ]
]
# Target

y = df["Risk"]

# Train/Test Split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Model

model = RandomForestClassifier()

model.fit(X_train, y_train)

# Save model

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained successfully!")
