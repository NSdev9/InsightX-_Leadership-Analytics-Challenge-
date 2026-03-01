from api_manager import call_openai

TABLE_SCHEMA = """
Table: upi_transactions

Columns:
- transaction_id
- timestamp
- transaction_type
- merchant_category
- amount_inr
- transaction_status
- sender_age_group
- receiver_age_group
- sender_state
- sender_bank
- receiver_bank
- device_type
- network_type
- fraud_flag
- hour_of_day
- day_of_week
- is_weekend
"""

def clean_sql(sql):
    if not sql:
        return None

    sql = sql.strip()

    if "```" in sql:
        parts = sql.split("```")
        for part in parts:
            if "select" in part.lower():
                sql = part
                break

    sql = sql.replace("sql", "").strip()

    if sql.endswith(";"):
        sql = sql[:-1]

    return sql.strip()


def generate_sql(question, context=""):

    lower_q = question.lower().strip()

    # 🔥 Identity Handling (Hardcoded – No DB)
    if "who created you" in lower_q:
        return "__IDENTITY_CREATED__"

    if lower_q in ["who are you", "what do you do", "tell me about yourself"]:
        return "__IDENTITY_SELF__"

    # 🔥 Non-dataset irrelevant guard
    irrelevant_keywords = [
        "weather", "movie", "politics", "cricket", "ipl", "celebrity",
        "history", "biology", "physics", "math problem"
    ]

    if any(word in lower_q for word in irrelevant_keywords):
        return "__IRRELEVANT__"

    prompt = f"""
You are InsightX — an elite fintech data intelligence system.

You MUST generate a valid DuckDB SELECT query ONLY if the question relates
to the UPI transactions dataset.

If the question is unrelated to:
- UPI
- transactions
- banking
- payments
- fraud
- merchant performance
- financial metrics

Return exactly:
NOT_RELEVANT

Use ONLY this schema:

{TABLE_SCHEMA}

Previous Question:
{context}

Current Question:
{question}

Rules:
- Only SELECT queries
- No INSERT, UPDATE, DELETE, DROP
- Use exact column names
- DuckDB compatible
- No explanation
- No markdown
- No semicolon
- If aggregation used → include GROUP BY
- If ranking insight → use ORDER BY DESC
- If financial metric asked → calculate properly
- Handle follow-up context logically

Return ONLY SQL query OR NOT_RELEVANT.
"""

    response = call_openai(prompt)

    if not response:
        return None

    raw_sql = response.choices[0].message.content.strip()

    if raw_sql == "NOT_RELEVANT":
        return "__IRRELEVANT__"

    cleaned_sql = clean_sql(raw_sql)

    if not cleaned_sql.lower().startswith("select"):
        return None

    return cleaned_sql