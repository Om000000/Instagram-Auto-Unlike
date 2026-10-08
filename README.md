# InstaUnlike Manager — Phase 2

A local web app for reviewing Instagram liked-post exports and recording your decisions.

## Phase 2 features
- Imports Instagram's `liked_posts.json` export format.
- Persistent SQLite statuses: `pending`, `unliked`, `kept`, `skipped`.
- One-at-a-time review queue.
- Open the exact Instagram URL in a new tab.
- Record Keep / Mark as Unliked / Skip.
- Automatic advance to the next pending post.
- Progress counters and search/status filters.
- Activity log for status changes.
- Migrates an existing Phase 1 database to support `kept`.

## Run
```bat
cd insta-unlike-manager\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000/

Java service is not required for the Phase 2 review UI.

## Safety boundary
The app does not request an Instagram password, log into Instagram, or automatically click Instagram controls. The user performs the Instagram action and then records the result in this app.
