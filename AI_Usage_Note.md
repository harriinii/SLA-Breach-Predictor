# AI Usage Note

## Project Name

AI-Powered SLA Breach Prediction System

---

## 1. How AI Was Used

Artificial Intelligence was used throughout the development process to accelerate design, implementation, debugging, and documentation.

### AI-Assisted Activities

#### 1. System Design

AI helped design the overall architecture of the system including:

* Ticket creation workflow
* SLA calculation logic
* Risk classification pipeline
* Dashboard structure
* WhatsApp notification flow

#### 2. LLM-Based Ticket Classification

AI assisted in creating prompts for ticket severity classification using Groq's Llama 3.3 model.

The model analyzes support ticket descriptions and assigns:

* Complexity Score (1–5)
* Priority Level
* Risk Category

#### 3. Code Generation

AI was used to generate and improve:

* Streamlit UI components
* SLA calculation functions
* CSV processing logic
* Ticket status workflows
* Plotly analytics charts
* Twilio notification integration

#### 4. Debugging Assistance

AI helped identify and resolve issues such as:

* Timezone mismatches
* Incorrect SLA countdown calculations
* Streamlit deployment issues
* DynamoDB integration errors
* Plotly visualization bugs
* Data persistence problems

#### 5. Documentation

AI assisted in creating:

* README.md
* Test Cases
* Architecture diagrams
* Workflow explanations
* Technical documentation

---

## 2. What AI Got Wrong

Although AI significantly accelerated development, several outputs required manual validation and correction.

### Incorrect Severity Classification

Initially, the AI model frequently returned:

* Complexity Score = 1
* Complexity Score = 5

for most tickets, causing poor classification quality.

This was resolved by:

* Refining the prompt
* Adding clearer scoring boundaries
* Providing realistic examples

---

### Incorrect Parsing Logic

AI originally generated parsing code expecting outputs such as:

```text
Priority: High
Complexity: 4
```

However, the model was instructed to return only:

```text
4
```

This mismatch caused all tickets to default to score 1.

Manual correction was required.

---

### Deployment Recommendations

AI initially suggested DynamoDB as a storage solution.

After reviewing challenge requirements:

* SQLite/PostgreSQL were more appropriate.
* Free-tier compatibility was improved using PostgreSQL-based solutions.

---

### UI Styling Issues

Several generated Plotly chart configurations caused:

```text
multiple values for keyword argument 'legend'
```

Manual debugging was required to resolve chart rendering issues.

---

## 3. Best Prompts Used

### Severity Classification Prompt

```text
You are an expert incident severity classifier.

Analyze support ticket comments and assign a complexity score from 1–5.

Consider:
- User impact
- Business impact
- Technical complexity
- Service availability

Return ONLY a single number.
```

---

### Risk Reason Generation Prompt

```text
Explain why this ticket is considered high risk.

Include:
- Business impact
- User impact
- SLA urgency

Return a concise operational explanation.
```

---

### README Generation Prompt

```text
Generate a professional GitHub README for an AI-Powered SLA Breach Prediction System.

Include:
- Architecture
- Workflow
- Features
- Screenshots
- Tech Stack
- Business Benefits
```

---

### Test Case Generation Prompt

```text
Generate software test cases covering:

- Manual ticket creation
- CSV upload
- SLA calculation
- Risk detection
- Status updates
- Analytics dashboard
```

---

## 4. Lessons Learned

Through this project, the team learned:

* Prompt engineering significantly impacts AI output quality.
* AI-generated code must always be reviewed and validated.
* LLMs are effective for ticket triage and operational support.
* Human oversight remains essential for production-quality systems.
* AI accelerates development but does not eliminate testing and debugging responsibilities.

---

## 5. Conclusion

AI played a major role in accelerating the development of the SLA Breach Prediction System by assisting with architecture design, coding, debugging, analytics generation, and documentation.

However, manual validation, testing, and refinement were necessary to ensure accuracy, reliability, and alignment with project requirements.

The final solution combines AI-driven ticket intelligence with traditional software engineering practices to create a practical and scalable SLA monitoring platform.
