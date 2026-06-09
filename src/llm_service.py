from groq import Groq
from dotenv import load_dotenv
import os
import streamlit as st
import re

load_dotenv()


def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)


client = Groq(api_key=get_secret("GROQ_API_KEY"))


def get_priority_from_complexity(score):
    if score == 5:
        return "Critical"
    elif score == 4:
        return "High"
    elif score == 3:
        return "Medium"
    else:
        return "Low"


def analyze_ticket(comment):
    prompt = f"""
You are an expert incident severity classifier with deep experience in SLA management and ticket triage.

Your task is to analyze support ticket comments and assign a complexity risk score from 1-5 that accurately reflects the actual severity and scope of the issue.

Scoring Framework:

1 = Cosmetic Issue (No operational impact)

Visual/UI problems: misalignment, spacing, font rendering
Text errors: typos, grammar, label mistakes
Display glitches that don't affect functionality
No users impacted beyond visual annoyance

2 = Isolated Customer Issue (Single user affected)

Problem affects one specific customer only
Workarounds exist or issue is user-specific
Examples: individual invoice download failure, single account profile update error
No systemic problem indicated

3 = Functional Bug (Multiple users, non-critical service)

Multiple users affected but core service still operational
Non-payment, non-authentication systems involved
Examples: export/report generation failing, search returning incorrect results, data filtering issues
Users can partially access the application

4 = Major Service Degradation (Widespread impact, critical paths affected)

Many users unable to complete key transactions
Payment processing, checkout, or revenue-impacting features down
API failures affecting integrations
Significant business revenue or user satisfaction at risk
Service is partially functional but critical paths broken

5 = Critical Outage (Complete service failure)

Production system completely unavailable
Database or core infrastructure failure
Authentication system down (users cannot log in)
Data loss or corruption
Entire application inaccessible to all users
Business operations halted

Critical Instructions:

Avoid extreme scoring: Don't default to 1 or 5. Most real issues fall in 2-4 range.
Look for scope indicators: "one customer" → likely 2, "many users" → likely 4, "some users" → likely 3
Distinguish between user count and impact severity: One user with payment failure might be 2, but many users unable to pay is 4
Consider system criticality: UI bugs are always low (1-2), payment/auth issues are always high (4-5)
If unclear, err toward the middle (3) rather than extremes

Ticket Comment:
{comment}

Output ONLY a single number (1, 2, 3, 4, or 5) with no additional text, explanation, or reasoning.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    print("LLM RAW RESPONSE:", result)

    match = re.search(r"\b[1-5]\b", result)

    if match:
        complexity_score = int(match.group())
    else:
        complexity_score = 3

    priority = get_priority_from_complexity(complexity_score)

    return priority, complexity_score