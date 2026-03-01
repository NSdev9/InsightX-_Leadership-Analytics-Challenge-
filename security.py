def validate_sql(sql):
    if not sql:
        return False

    sql_lower = sql.strip().lower()

    if not sql_lower.startswith("select"):
        print("SQL must start with SELECT")
        return False

    forbidden = ["drop", "delete", "update", "insert", "alter"]

    for word in forbidden:
        if word in sql_lower:
            return False

    return True