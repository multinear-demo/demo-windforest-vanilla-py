def format_cell_value(value):
    """Format a cell value for display in markdown table.

    Args:
        value: The value to format (can be any type)

    Returns:
        str: Formatted string representation of the value with thousand separators
    """
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def wrap_sql(sql: str, width: int = 60) -> str:
    """Wrap SQL query text at word boundaries.

    Args:
        sql: SQL query string to wrap
        width: Maximum line width (default: 60)

    Returns:
        Wrapped SQL string
    """
    words = sql.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def format_results_as_markdown_table(results):
    """Format SQL query results as a markdown table.

    Args:
        results: List of dictionaries containing query results

    Returns:
        str: Formatted markdown table string, or "No results found" message
    """
    if not results:
        return "\n**Results:** No results found."

    # Get column headers from the first result
    headers = list(results[0].keys())

    # Create markdown table header
    table = "| " + " | ".join(headers) + " |\n"
    # Add separator line
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    # Add data rows
    for row in results:
        table += (
            "| " + " | ".join(format_cell_value(row[col]) for col in headers) + " |\n"
        )

    return f"\n**Results:**\n{table}"
