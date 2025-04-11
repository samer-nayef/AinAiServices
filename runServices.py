import configparser
import json
import logging
import os
import sys
import time

import psycopg2 as psycopg2
import psycopg2.extras

from services import NerService, ClassifyService, dialectDetectionService, LanguageDetectionService, \
    sentimentAnalysisService

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

db_user = cfg.get('postgreconnection', 'db_user')
db_password = cfg.get('postgreconnection', 'db_password')
db_name = cfg.get('postgreconnection', 'db_name')
host = cfg.get('postgreconnection', 'host')
port = cfg.get('postgreconnection', 'port')
table = cfg.get('postgreconnection', 'table')

def open_connection():
    try:
        conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=host, port=port)
        # logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise



def runservice():
    try:
        raqim_video_text()
    except BaseException as e:
        # print(e)
        logger.error(str(e))


def raqim_video_text():
    conn = open_connection()

    add_column_if_not_exists(conn, "video", "raqimNerService", "JSONB")
    add_column_if_not_exists(conn, "video", "raqimClassifyService", "JSONB")
    add_column_if_not_exists(conn, "video", "raqimDetectLangService", "VARCHAR")
    add_column_if_not_exists(conn, "video", "raqimDialectService", "JSONB")
    add_column_if_not_exists(conn, "video", "raqimSentemintService", "JSONB")

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

        while True:
            # logger.info('start text raqim service')

            cur.execute(f"SELECT id,artext FROM {table} where updated_by_raqim = false and translated = TRUE and artext is not null order by creationdate DESC;")

            rows = cur.fetchall()

            if not rows:
                # logger.info("⏸️ No unprocessed videos. Sleeping for 5 minutes...")
                print("⏸️ No unprocessed videos. Sleeping for 5 minutes...")
                time.sleep(300)
                continue

            for row in rows:
                id = row.get('id')
                text = row.get('artext')



                nerResult = NerService.run(text=text)
                classifyResult = ClassifyService.run(text=text)
                dialectDetectionResult = dialectDetectionService.run(text=text)
                languageDetectionResult = LanguageDetectionService.run(text=text)
                sentimentAnalysisResult = sentimentAnalysisService.run(text=text)



                cur.execute(
                    f"""
                                        UPDATE {table} 
                                        SET updated_by_raqim = TRUE,
                                            raqimNerService = %s,
                                            raqimClassifyService = %s,
                                            raqimDetectLangService= %s,
                                            raqimDialectService = %s,
                                            raqimSentemintService = %s
                                        WHERE id = %s
                                        """,
                    (json.dumps(nerResult), json.dumps(classifyResult), json.dumps(languageDetectionResult), json.dumps(dialectDetectionResult), json.dumps(sentimentAnalysisResult), id)
                    # Pass values as parameters
                )
                conn.commit()
                print(f'raqim applied on: {id}')

            print(f'no records wait for 5 minutes')




def add_column_if_not_exists(conn, table_name, column_name, column_type="VARCHAR"):
    with conn.cursor() as cur:
        # Check if column exists
        cur.execute("""
            SELECT 1 FROM information_schema.columns 
            WHERE LOWER(table_name) = LOWER(%s) AND column_name = LOWER(%s)
        """, (table_name, column_name))
        column_exist = cur.fetchone()
        if not column_exist:
            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
            conn.commit()




if __name__ == "__main__":
    try:
        runservice()
    except Exception as ex:
        logger.error('run_service=====================' + str(ex))
        print("An error occurred. Please try again. Error: " + str(ex))

