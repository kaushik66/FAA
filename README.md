
# Fraud Analysis Agent (FAA) – LLM-Driven Banking Fraud Detection

## 1. Overview
Banking fraud detection is traditionally approached using machine learning classifiers that operate at the transaction level. While these models can achieve high precision, they often lack **human-like reasoning** and **contextual understanding**.

The **Fraud Analysis Agent (FAA)** addresses this by implementing an **LLM-orchestrated autonomous investigation framework**, inspired by the research paper [Fraud Analysis Agent: An LLM-Orchestrated Autonomous Fraud Investigation Framework](https://arxiv.org/abs/2506.11635).

Instead of simply classifying transactions as “fraud” or “not fraud,” FAA simulates the behavior of a **fraud investigator**—querying databases, plotting transaction histories, analyzing spending patterns, and writing reports before issuing a verdict.

---

## 2. Dataset

### Source
We used the **Sparkov synthetic credit card transaction dataset** generated via the [Sparkov Data Generation GitHub repository](https://github.com/namebrandon/Sparkov_Data_Generation).  
This dataset is entirely synthetic, meaning it poses no privacy concerns while still reflecting realistic transaction behaviors.

### Dataset Features
- **Transaction Details**: Amount, date, category, merchant, geolocation.
- **Customer Information**: Demographics, location, occupation, account profile.
- **Fraud Labels**: Binary `is_fraud` flag for each transaction.
- **Variety in Data**: Merchants in certain transactions have `fraud_` prefixes to simulate suspicious actors.

### Why Sparkov?
- Fully controllable data generation.
- Scalable for experiments.
- Well-structured with realistic patterns.
- Suitable for testing reasoning workflows without exposing sensitive real-world data.

---

## 3. Database Preparation
To allow the FAA agents to interact efficiently with the dataset, we converted the CSV output from Sparkov into a **SQLite database**.

**Steps:**
1. Generate transaction CSVs using Sparkov:
   ```bash
   python datagen.py -n 1000 -o synthetic_data 01-01-2025 12-31-2025
