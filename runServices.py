import configparser
import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from typing import List, Dict, Any

import psycopg2 as psycopg2
import psycopg2.extras
from psycopg2 import pool

from services import NerService, ClassifyService, dialectDetectionService, LanguageDetectionService, \
    sentimentAnalysisService, summarizationService

logging.basicConfig(
    level=logging.INFO,
    filename="debug.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#os.chdir(os.path.dirname(sys.argv[0]))
cfg = configparser.ConfigParser()
cfg.read('configuration.cfg')

# Database configuration
DB_CONFIG = {
    'dbname': cfg.get('postgreconnection', 'db_name'),
    'user': cfg.get('postgreconnection', 'db_user'),
    'password': cfg.get('postgreconnection', 'db_password'),
    'host': cfg.get('postgreconnection', 'host'),
    'port': cfg.get('postgreconnection', 'port')
}
TABLE_NAME = cfg.get('postgreconnection', 'table')

# Connection pool
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

def add_column_if_not_exists(conn, table_name: str, column_name: str, column_type: str = "VARCHAR") -> None:
    """Add a column to the table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1 FROM information_schema.columns 
            WHERE LOWER(table_name) = LOWER(%s) AND column_name = LOWER(%s)
        """, (table_name, column_name))
        if not cur.fetchone():
            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
            conn.commit()

def process_batch(rows: List[Dict[str, Any]], cur) -> None:
    """Process a batch of rows and update the database."""
    for row in rows:
        try:
            id = row.get('id')
            text = row.get('artext')
            
            # Run all services

            ner_result = NerService.run(text=text)
            classify_result = ClassifyService.run(text=text)
            language_detection_result = LanguageDetectionService.run(text=text)
            dialect_detection_result = None
            if language_detection_result.lower() == 'ar':
                dialect_detection_result = dialectDetectionService.run(text=text)

            sentiment_analysis_result = sentimentAnalysisService.run(text=text)
            summarization_result = summarizationService.run(text=text)

            # Update database
            cur.execute(
                f"""
                UPDATE {TABLE_NAME} 
                SET updated_by_raqim = TRUE,
                    raqimNerService = %s,
                    raqimClassifyService = %s,
                    raqimDetectLangService = %s,
                    raqimDialectService = %s,
                    raqimSentemintService = %s,
                    raqimSummarizationService = %s
                WHERE id = %s
                """,
                (
                    json.dumps(ner_result),
                    json.dumps(classify_result),
                    json.dumps(language_detection_result),
                    json.dumps(dialect_detection_result),
                    json.dumps(sentiment_analysis_result),
                    summarization_result,
                    id
                )
            )
            logger.info(f'Successfully processed record: {id}')
            
        except Exception as e:
            logger.error(f"Error processing record {id}: {str(e)}")
            continue

def raqim_video_text() -> None:
    """Main processing function for video text analysis."""
    with get_db_connection() as conn:
        # Ensure all required columns exist
        required_columns = {
            "raqimNerService": "JSONB",
            "raqimClassifyService": "JSONB",
            "raqimDetectLangService": "VARCHAR",
            "raqimDialectService": "JSONB",
            "raqimSentemintService": "JSONB",
            "raqimSummarizationService": "VARCHAR"
        }
        
        for column, type_ in required_columns.items():
            add_column_if_not_exists(conn, TABLE_NAME, column, type_)

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            while True:
                try:
                    # Fetch unprocessed records
                    cur.execute(
                        f"""
                        SELECT id, artext 
                        FROM {TABLE_NAME} 
                        WHERE updated_by_raqim = false 
                        AND translated = TRUE 
                        AND artext is not null 
                        ORDER BY creationdate DESC 
                        LIMIT 100
                        """
                    )
                    
                    rows = cur.fetchall()
                    
                    if not rows:
                        print("⏸️ No unprocessed videos. Sleeping for 5 minutes...")
                        logger.info("⏸️ No unprocessed videos. Sleeping for 5 minutes...")
                        time.sleep(300)
                        continue

                    # Process batch
                    process_batch(rows, cur)
                    conn.commit()
                    
                except Exception as e:
                    logger.error(f"Error in main processing loop: {str(e)}")
                    time.sleep(60)  # Wait a minute before retrying

def runservice() -> None:
    """Main service runner with proper error handling."""
    try:
        raqim_video_text()
    except Exception as e:
        logger.error(f"Service error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        runservice()
    except Exception as ex:
        logger.error(f'Service failed: {str(ex)}')
        print(f"An error occurred. Please check the logs. Error: {str(ex)}")
    finally:
        # Cleanup connection pool
        if 'connection_pool' in globals():
            connection_pool.closeall()

