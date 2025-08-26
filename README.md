# Fraud Analysis Agent (FAA)

## 📌 Overview
The **Fraud Analysis Agent (FAA)** is a Large Language Model (LLM)-powered fraud detection framework designed to simulate how a human fraud investigator works.  
Instead of directly classifying a transaction, FAA:
- Retrieves related transaction history.
- Analyzes spending patterns.
- Generates visual plots for anomalies.
- Produces a human-readable investigation report.
- Gives a final **Fraud / Not Fraud** verdict with a confidence score.

The project is based on the research paper:  
[Fraud Analysis Agent: An LLM-Orchestrated Autonomous Fraud Investigation Framework](https://arxiv.org/abs/2506.11635).

---

## 📂 Dataset
We use the **Sparkov synthetic credit card transactions dataset**, generated from the GitHub repository:  
[https://github.com/namebrandon/Sparkov_Data_Generation](https://github.com/namebrandon/Sparkov_Data_Generation)  

This dataset contains:
- Transaction details (`amount`, `category`, `merchant`, `date`, `location`)
- Customer details (`ssn`, `cc_num`, `name`, `dob`, `occupation`, `city_pop`, etc.)
- Fraud indicator (`is_fraud`)

---

## 🛠️ How It Works
The FAA system is made up of several components:

1. **Orchestrator Agent** – Plans the investigation and decides which tools to use.
2. **SQL Tool** – Retrieves relevant transaction data from a SQLite database.
3. **Vision Agent** – Generates plots showing spending patterns and anomalies.
4. **Report Generation Agent (RGA)** – Creates a natural language investigation report.
5. **Detective Agent** – Reads the report and outputs the final verdict and confidence score.

---

## 📦 Setup Instructions

## 2. Install Required Packages

From the project root directory, run:

```bash
pip install -r requirements.txt

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/kaushik66/FAA.git
cd FAA
   python datagen.py -n 1000 -o synthetic_data 01-01-2025 12-31-2025


