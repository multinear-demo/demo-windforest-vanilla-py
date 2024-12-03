from sqlalchemy import create_engine, text
import os
from typing import Dict
import json
from openai import AsyncOpenAI
from datetime import datetime


class TextToSQLEngine:
    """
    Text-to-SQL engine that converts natural language business questions
    into SQLite queries, executes them, and returns the query, rationale,
    and top 5 results.
    """

    def __init__(self):
        """
        Initialize the Text-to-SQL engine by setting up the database connection
        and OpenAI API key.
        """
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = AsyncOpenAI(api_key=api_key)

        # Initialize the SQLite database connection
        db_path = os.getenv("DATABASE_PATH", "sqlite:///data/windforest.db")
        self.engine = create_engine(db_path)

        # Define the OpenAI model to use
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")  # Updated to 'gpt-4'

        # Load the database schema
        self.schema = self._load_schema()

    def _load_schema(self) -> str:
        """
        Load the database schema from the generate.py file or define it manually.

        Returns:
            str: The database schema in SQL format.
        """
        schema = """
        -- Database Schema

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            segment TEXT,
            region TEXT,
            age INTEGER,
            gender TEXT,
            income_level REAL,
            clv REAL,
            account_creation_date DATE,
            preferred_contact_method TEXT,
            purchase_frequency TEXT,
            seasonal_preference TEXT,
            last_purchase_date DATE,
            avg_order_value REAL
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            title TEXT,
            department TEXT,
            manager_id INTEGER,
            hire_date DATE,
            termination_date DATE,
            salary REAL,
            bonus REAL,
            commission REAL,
            kpi_score REAL,
            shift TEXT,
            level INTEGER,
            FOREIGN KEY(manager_id) REFERENCES employees(id)
        );

        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            contact_name TEXT,
            address TEXT,
            rating REAL,
            location TEXT,
            contract_terms TEXT,
            relationship_length INTEGER
        );

        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT,
            parent_id INTEGER,
            popularity REAL,
            FOREIGN KEY(parent_id) REFERENCES categories(id)
        );

        CREATE TABLE authors (
            id INTEGER PRIMARY KEY,
            name TEXT
        );

        CREATE TABLE book_authors (
            book_id INTEGER,
            author_id INTEGER,
            PRIMARY KEY (book_id, author_id),
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(author_id) REFERENCES authors(id)
        );

        CREATE TABLE customer_service_interactions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_id INTEGER,
            interaction_date DATE,
            interaction_type TEXT,
            channel TEXT,
            priority TEXT,
            status TEXT,
            resolution_date DATE,
            satisfaction_score INTEGER,
            notes TEXT,
            employee_id INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        );

        CREATE TABLE book_categories (
            book_id INTEGER,
            category_id INTEGER,
            PRIMARY KEY (book_id, category_id),
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );

        CREATE TABLE book_price_history (
            id INTEGER PRIMARY KEY,
            book_id INTEGER,
            price REAL,
            effective_date DATE,
            end_date DATE,
            change_reason TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        );

        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            isbn TEXT,
            format TEXT,
            language TEXT,
            price REAL,
            stock_level INTEGER,
            safety_stock INTEGER,
            reorder_point INTEGER,
            publication_date DATE,
            supplier_id INTEGER,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        );

        CREATE TABLE shippers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            service_area TEXT,
            base_cost REAL,
            performance_rating REAL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            order_date DATE,
            status TEXT,
            shipping_method TEXT,
            payment_method TEXT,
            discount REAL,
            tax REAL,
            notes TEXT,
            customer_id INTEGER,
            employee_id INTEGER,
            shipper_id INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(employee_id) REFERENCES employees(id),
            FOREIGN KEY(shipper_id) REFERENCES shippers(id)
        );

        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            book_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        );
        """
        return schema

    async def process_query(self, user_question: str) -> Dict:
        """
        Process a user business question by converting it to an SQLite query,
        executing the query, and returning the query, rationale, and results.

        Args:
            user_question (str): The user's business question.

        Returns:
            Dict: A dictionary containing the SQL query, rationale, and results table.
        """
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Define the tool for SQL generation
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_sql_query",
                    "description": "Generate an SQL query based on the user's "
                                   "business question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rationale": {
                                "type": "string",
                                "description": "The reasoning behind the SQL query"
                                               "construction."
                            },
                            "query": {
                                "type": "string",
                                "description": "The SQL query to execute."
                            }
                        },
                        "required": ["query", "rationale"],
                        "additionalProperties": False,
                    }
                }
            }
        ]

        # Add business context from generate.py
        business_context = """
        Business Context:
        - Customers: Segmented into Retail, Wholesale, and VIP
          with varying purchase frequencies
        - Orders: Show seasonal patterns with peaks in November-December (holidays)
          and July-August (back to school)
        - Books: Managed with price history, categories, and multiple authors
        - Customer Service: Tracks interactions, satisfaction scores, and
          resolution times
        - Fraud Detection: Monitors for suspicious patterns like multiple
          same-day orders and unusual shipping
        - Inventory: Tracks stock levels, safety stock, and reorder points
        - Suppliers: Rated based on sales performance and stock management
        """

        # Prepare the prompt
        prompt = f"""
        You are an SQL expert.
        Convert the following business question into a precise SQLite query.
        Current date: {current_date}

        Database Schema:
        {self.schema}

        {business_context}

        User Question: {user_question}

        Important:
        - Return only valid SQLite syntax
        - Use appropriate JOINs for table relationships
        - Consider data patterns and business rules
        - Limit results to 5 rows unless specified otherwise
        """

        try:
            # Call OpenAI API with function calling
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in converting business questions "
                                   "into SQL queries."
                    },
                    {"role": "user", "content": prompt}
                ],
                tools=tools,
                tool_choice={"type": "function", "function": {
                    "name": "generate_sql_query"
                }}
            )

            # Extract the function response
            message = completion.choices[0].message
            if message.tool_calls:
                # Get the first tool call
                tool_call = message.tool_calls[0]
                # Safely parse the JSON arguments
                try:
                    arguments = json.loads(tool_call.function.arguments)
                    sql_query = arguments.get("query")
                    rationale = arguments.get("rationale")
                except json.JSONDecodeError as e:
                    return {"error": f"Failed to parse OpenAI response: {str(e)}"}
            else:
                return {"error": "No tool calls found in the response"}

            # Validate that we have both query and rationale
            if not sql_query or not rationale:
                return {"error": "Missing query or rationale in the response"}

            # Execute the SQL query with error handling
            try:
                with self.engine.connect() as connection:
                    result = connection.execute(text(sql_query))
                    rows = result.fetchmany(5)
                    columns = result.keys()

                # Format results as a list of dictionaries
                results_table = [dict(zip(columns, row)) for row in rows]

                return {
                    "query": sql_query,
                    "rationale": rationale,
                    "results": results_table
                }
            except Exception as e:
                return {"error": f"SQL execution failed: {str(e)}"}

        except Exception as e:
            return {"error": f"OpenAI API call failed: {str(e)}"}
