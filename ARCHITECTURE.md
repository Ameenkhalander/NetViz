# NetViz architecture

- `app.py`: Streamlit navigation, page rendering, quiz flow and analytics.
- `content.py`: curated nine-module lessons and protocol reference data.
- `database.py`: SQLite/PostgreSQL engine selection, schema initialisation and seed data.
- `models.py`: SQLAlchemy models for topics, questions, progress, attempts and custom questions.
- `components/diagrams.py`: reusable visual flow diagrams and OSI view.
- `components/ai_tutor.py`: optional OpenAI Responses API tutor and offline fallback.

## Data model
`topics` → `questions`; `lesson_progress` stores completion; `quiz_attempts` stores score/accuracy; `user_questions` stores locally created questions. `schema.sql` is a reference DDL; SQLAlchemy models are canonical.

## Security
Secrets are read from Streamlit Secrets or environment variables. ORM queries use SQLAlchemy. The packet simulator is visual-only. Practical labs require explicit user action and authorised targets.

## Production roadmap
Add login/authentication, per-user access control, moderation workflow, Alembic migrations, multi-select/scenario questions, persistent lab completion, question editing, rate limits and privacy controls.
