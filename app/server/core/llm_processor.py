import os
import random
from typing import Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from core.data_models import QueryRequest

def generate_sql_with_openai(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = OpenAI(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions
- For multi-table queries, use proper JOIN conditions to avoid Cartesian products
- Limit results to reasonable amounts (e.g., add LIMIT 100 for large result sets)
- When joining tables, use meaningful relationships between tables

SQL Query:"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Convert natural language to SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Error generating SQL with OpenAI: {str(e)}")

def generate_sql_with_anthropic(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions
- For multi-table queries, use proper JOIN conditions to avoid Cartesian products
- Limit results to reasonable amounts (e.g., add LIMIT 100 for large result sets)
- When joining tables, use meaningful relationships between tables

SQL Query:"""
        
        # Call Anthropic API
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        sql = response.content[0].text.strip()
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Error generating SQL with Anthropic: {str(e)}")

def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Format database schema for LLM prompt
    """
    lines = []
    
    for table_name, table_info in schema_info.get('tables', {}).items():
        lines.append(f"Table: {table_name}")
        lines.append("Columns:")
        
        for col_name, col_type in table_info['columns'].items():
            lines.append(f"  - {col_name} ({col_type})")
        
        lines.append(f"Row count: {table_info['row_count']}")
        lines.append("")
    
    return "\n".join(lines)

def generate_sql(request: QueryRequest, schema_info: Dict[str, Any]) -> str:
    """
    Route to appropriate LLM provider based on API key availability and request preference.
    Priority: 1) OpenAI API key exists, 2) Anthropic API key exists, 3) request.llm_provider
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Check API key availability first (OpenAI priority)
    if openai_key:
        return generate_sql_with_openai(request.query, schema_info)
    elif anthropic_key:
        return generate_sql_with_anthropic(request.query, schema_info)

    # Fall back to request preference if both keys available or neither available
    if request.llm_provider == "openai":
        return generate_sql_with_openai(request.query, schema_info)
    else:
        return generate_sql_with_anthropic(request.query, schema_info)

def generate_natural_language_query(schema_info: Dict[str, Any], complexity: str = "simple") -> tuple[str, str]:
    """
    Generate interesting natural language query based on database schema.
    Returns tuple of (query, context).
    Uses higher temperature (0.8) to ensure variety.
    """
    if not schema_info.get('tables'):
        raise ValueError("No tables available in database")

    # Get available API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Format schema for prompt
    schema_description = format_schema_for_prompt(schema_info)

    # Create query type suggestions for variety
    query_types = [
        "filtering data with specific conditions",
        "aggregating data with GROUP BY and COUNT/SUM/AVG",
        "finding top N records ordered by a column",
        "joining multiple tables to combine data",
        "filtering by date ranges or time periods",
        "finding unique or distinct values",
        "searching for patterns in text columns",
        "calculating statistics or percentages",
    ]

    suggested_type = random.choice(query_types)

    # Create prompt for generating natural language query
    prompt = f"""Given the following database schema:

{schema_description}

Generate an interesting natural language query that a user might ask about this data. The query should be:
- Concise (maximum 2 sentences)
- Specific and actionable
- Focus on {suggested_type}
- Relevant to the actual columns and tables available
- {'Simple and straightforward' if complexity == 'simple' else 'More complex with multiple conditions'}

Return ONLY the natural language query, nothing else. Do not include explanations or SQL.

Natural language query:"""

    try:
        # Try OpenAI first
        if openai_key:
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a data analyst helping users explore their data. Generate natural language queries that users can ask."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher temperature for variety
                max_tokens=150
            )
            query = response.choices[0].message.content.strip()
        elif anthropic_key:
            client = Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.8,  # Higher temperature for variety
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            query = response.content[0].text.strip()
        else:
            raise ValueError("No API key available for OpenAI or Anthropic")

        # Clean up query (remove quotes if present)
        query = query.strip('"').strip("'")

        # Ensure query is max 2 sentences
        sentences = query.split('.')
        if len(sentences) > 2:
            query = '.'.join(sentences[:2]).strip() + '.'

        # Generate context explaining what the query does
        context = f"This query focuses on {suggested_type} using the available data."

        return query, context

    except Exception as e:
        # Fallback to generic queries if LLM fails
        table_names = list(schema_info.get('tables', {}).keys())
        if not table_names:
            raise ValueError("No tables available")

        table_name = random.choice(table_names)
        table_info = schema_info['tables'][table_name]
        columns = list(table_info['columns'].keys())

        fallback_queries = [
            f"Show me all records from {table_name}",
            f"Count the total number of records in {table_name}",
            f"Show me the first 10 records from {table_name}",
        ]

        if len(columns) > 1:
            col = random.choice(columns)
            fallback_queries.extend([
                f"Show me unique values in the {col} column from {table_name}",
                f"Group {table_name} by {col} and count each group",
            ])

        query = random.choice(fallback_queries)
        context = "This is a basic query to help you explore your data."

        return query, context