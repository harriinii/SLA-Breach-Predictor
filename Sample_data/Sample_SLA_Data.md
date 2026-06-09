# Sample Data Documentation

This directory contains anonymized ITSM Incident and SLA logs used for training and evaluating the SLA Breach Prediction System. Below is a structured snapshot representation of the features contained in `raw_incidents.csv`.

### Training Set Snapshot (`sample_features.csv`)

| Incident_ID | Priority | Category | Open_To_Breach_Mins | Sys_Escalation_Count | Short_Description | SLA_Breached (Target) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| INC0038421 | 1 - Critical | Network Hardware | 240 | 0 | "Core switch down in Building 4, site isolated." | 1 |
| INC0038422 | 3 - Moderate | Access/IAM | 1440 | 1 | "Reset LDAP password for user account." | 0 |
| INC0038423 | 2 - High | Database | 480 | 0 | "SQL Replica sync failure, lag increasing." | 1 |
| INC0038424 | 4 - Low | Software | 2880 | 0 | "Update MS Teams local application patch." | 0 |
| INC0038425 | 2 - High | Security ERP | 480 | 2 | "SAP Ledger module locking out accounting team."| 1 |

### Feature Descriptions
* `Incident_ID`: Unique key from the ticketing system.
* `Priority`: Categorical importance scaling from 1 (Critical) to 4 (Low).
* `Open_To_Breach_Mins`: Calculated dynamic timeframe until the SLA threshold expires.
* `Sys_Escalation_Count`: Number of times the ticket was passed up the tier architecture.
* `Short_Description`: Raw string input passed directly to the TF-IDF / Embeddings pipeline.
* `SLA_Breached`: The target binary classification label (`1` = Breach Occurred, `0` = Closed in Compliance).