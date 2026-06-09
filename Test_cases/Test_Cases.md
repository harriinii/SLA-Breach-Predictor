# Test Cases - AI-Powered SLA Breach Prediction System

## Test Case 1: Manual Ticket Creation

### Objective
Verify that a support engineer can create a ticket manually.

### Input

```text
Customer Name: Ravi
Comment: One customer cannot download their invoice.
```

### Expected Output

```text
Ticket created successfully
Status = Open
Complexity Score = 2
Priority = Low
SLA Deadline generated
```

---

## Test Case 2: CSV Upload

### Objective
Verify that multiple tickets can be uploaded using a CSV file.

### Input

```csv
customer_name,comment
Ram,The company logo is slightly misaligned on the login page.
Ravi,One customer cannot download their invoice.
Suresh,Several users are unable to export reports.
Karthik,Checkout is failing for many customers during payment.
Priya,The production database has crashed and all users are unable to access the application.
```

### Expected Output

```text
All rows processed successfully
Tickets stored in system
Existing tickets retained
New tickets appended
```

---

## Test Case 3: AI Complexity Classification

### Objective
Verify correct AI severity classification.

| Ticket Comment | Expected Complexity | Expected Priority |
|---------------|-------------------|------------------|
| Logo alignment issue | 1 | Low |
| One customer cannot download invoice | 2 | Low |
| Several users unable to export reports | 3 | Medium |
| Checkout failing for many customers | 4 | High |
| Production database crash | 5 | Critical |

### Expected Output

```text
AI returns correct complexity score and priority.
```

---

## Test Case 4: SLA Deadline Calculation

### Objective
Verify SLA deadline generation.

| Priority | SLA Hours |
|----------|-----------|
| Low | 24 |
| Medium | 8 |
| High | 4 |
| Critical | 2 |

### Expected Output

```text
Deadline = Created Time + SLA Hours
```

---

## Test Case 5: Risk Status Detection

### Objective
Verify risk classification logic.

| Condition | Expected Risk |
|-----------|---------------|
| Remaining Time > 60 mins | Normal |
| Remaining Time < 60 mins | CRITICAL BREACH RISK |
| Remaining Time < 0 | Breached |
| Status = Resolved/Closed | Completed |

### Expected Output

```text
Risk status calculated correctly.
```

---

## Test Case 6: Active Ticket Dashboard

### Objective
Verify active ticket display.

### Expected Output

```text
Open tickets visible
In Progress tickets visible
Resolved tickets hidden
Closed tickets hidden
```

---

## Test Case 7: Ticket Status Update

### Objective
Verify ticket lifecycle transitions.

### Steps

```text
Open
↓
In Progress
↓
Resolved
↓
Closed
```

### Expected Output

```text
Status updated successfully.
```

---

## Test Case 8: Critical Alert Generation

### Objective
Verify critical alert creation.

### Input

```text
Checkout is failing for many customers during payment.
```

### Expected Output

```text
Complexity Score = 4
Priority = High
Alert generated
Risk Status = CRITICAL BREACH RISK
```

---

## Test Case 9: WhatsApp Notification

### Objective
Verify Twilio WhatsApp alert functionality.

### Condition

```text
Remaining Minutes < 60

OR

Complexity Score >= 4
```

### Expected Output

```text
WhatsApp alert sent successfully.
```

---

## Test Case 10: Analytics Dashboard

### Objective
Verify analytics calculations.

### Expected Output

```text
Priority Distribution Chart
Risk Status Chart
Complexity Score Distribution
Resolution Rate
Average Complexity
Average SLA Window
Breach Rate
```

---

## Test Case 11: Resolved & Closed Records

### Objective
Verify completed ticket archival.

### Steps

```text
Update ticket to Resolved
OR
Update ticket to Closed
```

### Expected Output

```text
Ticket moved to Resolved & Closed page
Ticket removed from Active Dashboard
Ticket still counted in Total Tickets
```

---

## Test Case 12: Invalid CSV Validation

### Objective
Verify invalid CSV handling.

### Input

```csv
name,issue
Ram,Application Down
```

### Expected Output

```text
Error Message:
CSV must contain customer_name and comment columns.
```

---

# Integration Test Case

### Objective
Verify complete end-to-end workflow.

### Steps

```text
Upload CSV
↓
Read customer_name and comment
↓
Analyze ticket using Groq LLM
↓
Generate complexity score
↓
Assign priority
↓
Calculate SLA deadline
↓
Store ticket
↓
Display in dashboard
↓
Evaluate breach risk
↓
Generate alert if critical
↓
Update status
↓
Move to Resolved & Closed page
```

### Expected Output

```text
Entire workflow executes successfully without errors.
```

---

# Test Coverage Summary

| Module | Tested |
|----------|---------|
| Manual Ticket Creation | ✅ |
| CSV Upload | ✅ |
| AI Classification | ✅ |
| Priority Assignment | ✅ |
| SLA Calculation | ✅ |
| Risk Detection | ✅ |
| Dashboard Display | ✅ |
| Status Update | ✅ |
| Critical Alerts | ✅ |
| WhatsApp Notifications | ✅ |
| Analytics Dashboard | ✅ |
| Historical Records | ✅ |
| CSV Validation | ✅ |
| End-to-End Workflow | ✅ |

---

## Result

```text
All core functionalities of the AI-Powered SLA Breach Prediction System
have been validated through functional, integration, and happy-path test cases.
```
