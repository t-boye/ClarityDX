# run_migrations.py
# This script is responsible for applying database schema migrations.
# It reads SQL files from the 'migrations' directory and tracks applied versions
# in a 'schema_migrations' table in the database.

import os
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file (for local development)
# On Render, these will be supplied directly by the platform.
load_dotenv()

# Configure logging for clear output during migration process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection() -> psycopg2.extensions.connection:
    """
    Establishes a single database connection for migration purposes.
    It retrieves connection details from environment variables.
    """
    try:
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")
        db_host = os.environ.get("DB_HOST")
        db_port = os.environ.get("DB_PORT", "5432") # Default to 5432 if DB_PORT is not set
        ssl_mode = 'require' # Crucial for connecting to Render PostgreSQL externally or internally

        # Validate that all necessary environment variables are present
        if not all([db_name, db_user, db_password, db_host]):
            raise ValueError(
                "Missing database environment variables. "
                "Ensure DB_NAME, DB_USER, DB_PASSWORD, and DB_HOST are set."
            )

        logging.info(f"Attempting to connect to DB: {db_user}@{db_host}:{db_port}/{db_name}")

        # Establish the database connection
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            sslmode=ssl_mode
        )
        logging.info("Successfully established database connection.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database for migrations: {e}")
        # Re-raise the exception so the calling context knows about the failure
        raise

def apply_migrations():
    """
    Applies pending SQL migration files to the database.
    It uses a 'schema_migrations' table to track which migration versions
    have already been applied to the database.
    """
    conn = None
    cur = None
    try:
        # Get a database connection
        conn = get_db_connection()
        # Create a cursor to execute SQL commands
        cur = conn.cursor()

        # Ensure the 'schema_migrations' table exists. This table tracks which
        # migration files have already been applied to prevent re-running them.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit() # Commit the creation of the schema_migrations table
        logging.info("Ensured 'schema_migrations' table exists.")

        # Retrieve a list of already applied migration versions from the database
        cur.execute("SELECT version FROM schema_migrations")
        applied_versions = {row[0] for row in cur.fetchall()}
        logging.info(f"Already applied migrations: {applied_versions}")

        # Define the path to the migrations directory
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

        # Get all SQL files in the migrations directory, sorted by name
        # (e.g., V001_initial_schema.sql, V002_add_column.sql)
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])

        if not migration_files:
            logging.info(f"No SQL migration files found in the '{migrations_dir}' directory. Nothing to apply.")
            return # Exit if no migration files are found

        # Iterate through each migration file
        for filename in migration_files:
            version = os.path.splitext(filename)[0] # Extract the version name (e.g., 'V001_initial_schema')
            
            # Check if this migration version has already been applied
            if version not in applied_versions:
                filepath = os.path.join(migrations_dir, filename)
                logging.info(f"Attempting to apply migration: {filename}")
                try:
                    # Read the SQL script content from the file
                    with open(filepath, 'r') as f:
                        sql_script = f.read()
                    
                    # Execute the SQL script. Your SQL file contains BEGIN/COMMIT,
                    # so it manages its own transaction.
                    cur.execute(sql_script)
                    
                    # Record this migration as applied in the schema_migrations table
                    cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
                    conn.commit() # Commit the changes for this specific migration
                    logging.info(f"Successfully applied {filename}")
                except psycopg2.Error as e:
                    # If an error occurs during migration, rollback the transaction
                    conn.rollback()
                    logging.error(f"Error applying migration {filename}: {e}")
                    # Re-raise the exception to stop the migration process and indicate failure
                    raise
            else:
                logging.info(f"Migration {filename} already applied. Skipping.")

    except Exception as e:
        # Catch any critical errors during the overall migration process
        logging.critical(f"Database migration process failed critically: {e}")
        if conn:
            conn.rollback() # Ensure any pending transaction is rolled back
        raise # Re-raise to propagate the error to the calling environment
    finally:
        # Ensure the cursor and connection are closed in all cases
        if cur:
            cur.close()
        if conn:
            conn.close()
        logging.info("Database migration process finished.")

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    logging.info("Starting database migrations...")
    try:
        apply_migrations()
        logging.info("All database migrations completed successfully.")
    except Exception:
        # If any exception occurred during apply_migrations, log it and exit with an error code
        logging.error("Database migrations failed. Please check the logs above for details.")
        exit(1) # Exit with a non-zero status code to indicate failure
