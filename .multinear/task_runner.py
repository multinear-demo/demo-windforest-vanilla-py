import sys
import asyncio
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import necessary components
# ruff: noqa: E402
from engine import TextToSQLEngine
from formatters import wrap_sql, format_results_as_markdown_table

from dotenv import load_dotenv

load_dotenv()

# Initialize Text-to-SQL engine (consider if singleton is needed here)
# For a simple task runner, initializing per run might be okay,
# but initialize outside the function if the runner handles multiple tasks.
sql_engine = TextToSQLEngine()


def run_task(input: str):
    """
    Process the input user question using the Text-to-SQL engine.

    Args:
        input (str): The user question to process.

    Returns:
        dict: A dictionary containing the response and sources (SQL query).
              Returns an error dictionary if processing fails.
    """
    # Process the query using Text-to-SQL engine
    # Use asyncio.run to call the async function from this sync function
    sql_result = asyncio.run(sql_engine.process_query(input))

    # Format the response
    if "error" in sql_result:
        # Return error information
        return {"error": sql_result["error"]}
    else:
        # Format successful response
        results_text = format_results_as_markdown_table(sql_result["results"])
        response = (
            f"Based on your question, I ran the following SQL query:\n"
            f"```sql\n{wrap_sql(sql_result['query'])}\n```\n\n"
            f"**Rationale:** {sql_result['rationale']}\n"
            f"{results_text}"
        )

        return {"output": response, "details": {"model": sql_engine.model}}
