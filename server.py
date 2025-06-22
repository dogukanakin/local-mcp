import psycopg2
import argparse
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('postgresql-demo')

# PostgreSQL connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'mcp_example',
    'user': 'postgres',
    'password': 'postgres'
}

def init_db():
    """Connect to the PostgreSQL database and create the table if it doesn't exist."""
    conn = psycopg2.connect(**DB_CONFIG)
    db_executor = conn.cursor()
    
    # Create the people table
    db_executor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INTEGER NOT NULL,
            profession VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn, db_executor

@mcp.tool()
def add_data(query: str) -> bool:
    """Add new data to the people table using a SQL INSERT query.

    Args:
        query (str): SQL INSERT query in the format:
            INSERT INTO people (name, age, profession) VALUES ('John Doe', 30, 'Engineer')
            
            For multiple records:
            INSERT INTO people (name, age, profession) VALUES 
            ('John Doe', 30, 'Engineer'),
            ('Jane Smith', 25, 'Developer')
        
    Schema:
        - name: Text field (required)
        - age: Integer field (required)
        - profession: Text field (required)
        Note: 'id' and 'created_at' are auto-generated
    
    Returns:
        bool: True if data was added successfully, False otherwise
    
    Example:
        >>> query = "INSERT INTO people (name, age, profession) VALUES ('Alice Smith', 25, 'Developer')"
        >>> add_data(query)
        True
    """
    try:
        conn, db_executor = init_db()
        
        # Clean the query - remove backslashes
        cleaned_query = query.replace('\\', '').strip()
        
        # Print the query for debugging
        print(f"Executing SQL: {cleaned_query}")
        
        db_executor.execute(cleaned_query)
        conn.commit()
        
        # Get the number of affected rows
        rows_affected = db_executor.rowcount
        conn.close()
        
        print(f"✅ {rows_affected} records added successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"PostgreSQL Error: {e}")
        print(f"Problematic SQL: {query}")
        return False
    except Exception as e:
        print(f"General Error: {e}")
        return False

@mcp.tool()
def add_person(name: str, age: int, profession: str) -> bool:
    """A safe function to add a single person.
    
    Args:
        name (str): The person's name
        age (int): The person's age
        profession (str): The person's profession
    
    Returns:
        bool: True if successful
    
    Example:
        >>> add_person("John Doe", 30, "Engineer")
        True
    """
    try:
        conn, db_executor = init_db()
        
        # Use parameterized query (protection against SQL injection)
        db_executor.execute(
            "INSERT INTO people (name, age, profession) VALUES (%s, %s, %s)",
            (name, age, profession)
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully added '{name}'!")
        return True
        
    except psycopg2.Error as e:
        print(f"PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"General Error: {e}")
        return False

@mcp.tool()
def read_data(query: str = "SELECT * FROM people ORDER BY id") -> list:
    """Read data from the people table in PostgreSQL.

    Args:
        query (str, optional): SQL SELECT query. 
            Defaults to: "SELECT * FROM people ORDER BY id"
            Examples:
            - "SELECT * FROM people"
            - "SELECT name, age FROM people WHERE age > 25"
            - "SELECT * FROM people ORDER BY age DESC"
            - "SELECT COUNT(*) FROM people"
    
    Returns:
        list: A list of tuples containing the query results.
              For the default query, format is: (id, name, age, profession, created_at)
    
    Example:
        >>> # Read all records
        >>> read_data()
        [(1, 'John Doe', 30, 'Engineer', '2024-01-15 10:30:00'), ...]
        
        >>> # With a custom query
        >>> read_data("SELECT name, profession FROM people WHERE age < 30")
        [('Alice Smith', 'Developer')]
    """
    try:
        conn, db_executor = init_db()
        db_executor.execute(query)
        results = db_executor.fetchall()
        conn.close()
        return results
    except psycopg2.Error as e:
        print(f"PostgreSQL Error: {e}")
        return []
    except Exception as e:
        print(f"General Error: {e}")
        return []

@mcp.tool()
def get_table_info() -> dict:
    """Get information about the people table.
    
    Returns:
        dict: Table structure and statistics
    """
    try:
        conn, db_executor = init_db()
        
        # Get table structure
        db_executor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'people'
            ORDER BY ordinal_position
        """)
        columns = db_executor.fetchall()
        
        # Get record count
        db_executor.execute("SELECT COUNT(*) FROM people")
        count = db_executor.fetchone()[0]
        
        conn.close()
        
        return {
            "table_name": "people",
            "columns": columns,
            "record_count": count,
            "database": "PostgreSQL (mcp_example)"
        }
    except psycopg2.Error as e:
        print(f"PostgreSQL Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting PostgreSQL MCP Server...")
    print(f"🔗 Database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    # Test the connection
    try:
        conn, db_executor = init_db()
        print("✅ PostgreSQL connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type) 