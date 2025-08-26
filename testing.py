# test_faa.py
import sqlite3
import random
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from faa import run_faa  # assuming your faa.py exposes run_faa function

# --- CONFIG ---
DB_PATH = "faa.sqlite"
TEST_CASES = 50

def get_random_test_cases():
    conn = sqlite3.connect(DB_PATH)
    # Query fraud and non-fraud transactions separately
    fraud_df = pd.read_sql("SELECT trans_num, is_fraud FROM transactions WHERE is_fraud = 1", conn)
    nonfraud_df = pd.read_sql("SELECT trans_num, is_fraud FROM transactions WHERE is_fraud = 0", conn)
    n = TEST_CASES // 2
    # Randomly sample n rows from each category
    fraud_sample = fraud_df.sample(n, random_state=42) if len(fraud_df) >= n else fraud_df
    nonfraud_sample = nonfraud_df.sample(n, random_state=42) if len(nonfraud_df) >= n else nonfraud_df
    # Concatenate and shuffle
    balanced_df = pd.concat([fraud_sample, nonfraud_sample], ignore_index=True)
    balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
    conn.close()
    return balanced_df

def evaluate_model():
    test_data = get_random_test_cases()
    y_true = []
    y_pred = []

    for _, row in test_data.iterrows():
        trans_num = row["trans_num"]
        if pd.isna(row["is_fraud"]):
            continue
        actual_fraud = int(row["is_fraud"])
        y_true.append(actual_fraud)

        # Run FAA investigation and get verdict
        verdict, confidence = run_faa(case_id=trans_num, max_steps=5, return_verdict=True)
        
        # Convert verdict to binary 1/0
        threshold = 0.7
        pred = 1 if verdict.lower() == "fraud" and confidence >= threshold else 0
        y_pred.append(pred)

    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print("Confusion Matrix:")
    print(cm)

    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred))

if __name__ == "__main__":
    evaluate_model()