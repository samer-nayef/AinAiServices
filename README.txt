Ain_RaqimAiServices

What this project does
- This worker polls a PostgreSQL table for unprocessed Arabic text rows and enriches each row using external AI HTTP services: language detection, dialect detection, NER, text classification, sentiment analysis, and summarization. Results are written back as JSON fields on the same row.
- It is designed to run continuously, batching records and retrying on transient failures while logging errors to a file.

Project structure (key files)
- runServices.py                Main long‑running worker: DB polling loop, calls services, writes results
- configuration.cfg             Central config: DB creds/table, API base URL and endpoints, tokens, timing
- constants.py                  Service endpoints, labels, languages and defaults used by service clients
- services/                     Service clients (HTTP callers) and helpers
  - NerService.py               Named Entity Recognition client
  - ClassifyService.py          Text classification client
  - LanguageDetectionService.py Language detection client
  - dialectDetectionService.py  Arabic dialect detection client
  - sentimentAnalysisService.py Sentiment analysis client
  - summarizationService.py     Summarization client
  - translateService.py         Translation client
  - utils.py                    Shared HTTP/session, chunking, config, and small helpers
- debug.log                     Log file (errors only recommended)
- auth/tokenGenerator.py        Token utility (if used)

Setup
- Requirements (Python 3.10+ suggested):
  - requests, psycopg2, urllib3, cryptography (see your virtualenv under env/ for exact versions)
- Recommended virtualenv
  - python3 -m venv env
  - source env/bin/activate
  - pip install requests psycopg2-binary cryptography

Configuration
- Edit configuration.cfg (mask secrets in commits):
  [postgreconnection]
  db_user=postgres
  db_password=********
  db_name=ain
  table=video
  host=localhost
  port=5432

  [token]
  key = ************************
  text = **********************
  value = ************************
  csrf = ************************

  [urls]
  SERVER=http://HOST:PORT
  NER=/ner/predict/
  CLASSIFY=/classify/predict/
  DIALECT_DECT=/dialect_detection/predict/
  LANG_DECT=/language_detection/predict/
  SENTIMENT_ANALYSIS=/sentiment_analysis/predict/
  TRANSLATE=/translation/predict/
  SUMMARIZE=/summarize/predict/

  [text_processing]
  CHUNK_SIZE=500
  OVERLAP_SIZE=50

  [http_settings]
  MAX_RETRIES=3
  TIMEOUT=30
  CACHE_SIZE=1000

- Where to put secrets/URLs: Keep them only in configuration.cfg. Do not hardcode in code.

How to run
- Ensure PostgreSQL is reachable and the target table exists with expected columns.
- Activate the virtualenv and run:
  - source env/bin/activate
  - python runServices.py
- The worker will start polling and writing results. Logs go to debug.log.

Operational behavior
- Poll loop (runServices.py):
  - Opens a pooled DB connection.
  - Ensures required JSON columns exist on the table.
  - SELECTs up to 100 unprocessed rows (translated = TRUE, text not null) ordered by newest.
  - For each row: calls services in sequence (language, dialect if Arabic, NER, classify, sentiment, summarize) and updates the row.
  - On empty queue: sleeps 5 minutes, then polls again.
  - On errors: logs error and continues; main loop sleeps 60 seconds before retrying if the loop itself fails.

Troubleshooting
- DB connection errors: verify [postgreconnection] in configuration.cfg and DB network access.
- HTTP 4xx/5xx to services: verify SERVER and endpoint paths in [urls], and tokens in [token].
- Sentiment error "unhashable type": ensure you are on the latest code; avoid caching the session/headers in LRU.
- Infinite loop while chunking: set OVERLAP_SIZE < CHUNK_SIZE.
- Missing Python packages: pip install requests psycopg2-binary cryptography.
- Nothing is processed: confirm table, flags (updated_by_raqim = false, translated = TRUE), and that artext is not null.

Security notes
- Do NOT commit real secrets: configuration.cfg should be masked/redacted before commits.
- Do NOT commit env/, __pycache__/ or debug.log to source control.
- Rotate tokens/CSRF if exposed and prefer environment-specific copies of configuration.cfg.

Notes on logging
- Logging is written to debug.log. For production, configure logging to ERROR level only.
- Suggestion (optional): a RotatingFileHandler can be added to limit file size, but is not enabled by default here.
