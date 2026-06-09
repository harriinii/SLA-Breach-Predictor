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


def normalize_score(comment, raw_score):
    comment_lower = comment.lower()

    level_5_keywords = [
        "complete outage",
        "entire application down",
        "system down",
        "production down",
        "all users",
        "everyone unable",
        "cannot login",
        "authentication down",
        "database down",
        "database failure",
        "data loss",
        "data corruption",
        "business halted",
        "service unavailable",
        "application inaccessible",
        "critical outage"
    ]

    level_4_keywords = [
        "many users",
        "multiple users",
        "payment failed",
        "payment failure",
        "checkout failed",
        "api failure",
        "major impact",
        "revenue impact",
        "critical path",
        "service degradation"
    ]

    low_keywords = [
        "typo",
        "alignment",
        "font",
        "color",
        "ui issue",
        "button color",
        "spelling",
        "cosmetic"
    ]

    if any(keyword in comment_lower for keyword in level_5_keywords):
        return 5

    if any(keyword in comment_lower for keyword in level_4_keywords):
        return max(raw_score, 4)

    if any(keyword in comment_lower for keyword in low_keywords):
        return min(raw_score, 2)

    return raw_score


def analyze_ticket(comment):
    prompt = f"""
You are an expert SLA incident severity classifier.

Classify the ticket into EXACTLY one complexity score from 1 to 5.

Important:
Return ONLY one number.
Do not explain.
Do not write priority.
Do not write JSON.
Do not write markdown.

Scoring rules:

1 = Cosmetic issue
- UI alignment
- typo
- spelling mistake
- color/font/display issue
- no functional impact

2 = Isolated customer issue
- only one customer affected
- user-specific issue
- workaround available
- no system-wide problem

3 = Functional bug
- multiple users affected
- feature partially working
- non-critical module issue
- reports, search, filters, export problems

4 = Major service degradation
- many users affected
- payment/checkout/API issue
- revenue-impacting feature broken
- critical business flow partially broken
- service still partially available

5 = Critical outage
Use 5 ONLY when one or more of these are clearly true:
- complete production outage
- entire application unavailable
- all users affected
- authentication/login system down for all users
- database/core infrastructure failure
- data loss or data corruption
- business operations completely stopped
- no workaround exists

Decision examples:
"All users cannot login to production" -> 5
"Database is down and app is inaccessible" -> 5
"Payment failed for many users" -> 4
"Checkout is failing for multiple customers" -> 4
"Report export not working for some users" -> 3
"One customer cannot download invoice" -> 2
"Button alignment issue" -> 1

Ticket:
{comment}

Answer only 1, 2, 3, 4, or 5.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a strict SLA classifier. You must output only one digit from 1 to 5."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=5
    )

    result = response.choices[0].message.content.strip()

    print("LLM RAW RESPONSE:", result)

    match = re.search(r"\b[1-5]\b", result)

    if match:
        complexity_score = int(match.group())
    else:
        complexity_score = 3

    complexity_score = normalize_score(comment, complexity_score)

    complexity_score = max(1, min(5, complexity_score))

    priority = get_priority_from_complexity(complexity_score)

    return priority, complexity_score


def generate_risk_reason(comment, complexity_score, remaining_minutes):
    prompt = f"""
You are an SLA Risk Analyst.

Ticket Comment:
{comment}

Complexity Score:
{complexity_score}

Remaining SLA Minutes:
{remaining_minutes}

Explain in ONE short sentence why this ticket is risky.

Rules:
- If remaining minutes is negative, mention SLA already breached.
- If remaining minutes is less than 60, mention deadline risk.
- If complexity score is 5, mention critical outage or severe business impact.
- If complexity score is 4, mention major service degradation or business impact.
- Return only one sentence.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You explain SLA risk in one short sentence."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=60
    )

    return response.choices[0].message.content.strip()