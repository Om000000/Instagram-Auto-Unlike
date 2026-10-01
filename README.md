# InstaUnlike Manager

Local-first, cloud-ready web application for importing Instagram liked-post exports and tracking user-confirmed unlike actions.

## Stack
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Python: Flask REST API, JSON importer, SQLite database owner
- Java: Java 17 HTTP service foundation for workflow orchestration
- Database: SQLite
- Communication: REST/JSON

**Database design:** Python is the sole SQLite owner. Java communicates with Python over HTTP in later phases rather than opening the same SQLite file independently. This avoids competing database connections and duplicated business logic.

## Requirements
- Python 3.10+
- Java 17+
- Browser

## Start Python
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Start Java (second terminal)
```bash
cd java-service
javac -d out src/main/java/com/instaunlike/JobService.java
java -cp out com.instaunlike.JobService
```
Java health: http://127.0.0.1:8080/api/health

## Instagram data
Download your Instagram information from Accounts Center in JSON format with Likes included. This app imports the export and does not ask for your Instagram password. Export formats vary; Phase 2 can adapt the parser to a sanitized sample.

The app does not automate Instagram clicks. A post is only considered unliked after you perform the action on Instagram and confirm it in the app.
