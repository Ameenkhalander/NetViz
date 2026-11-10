# NetViz — Networking & Cybersecurity Learning Platform

A Streamlit portfolio project for visual learning across networking protocols, SOC fundamentals and authorised penetration-testing practice.

## Included
- Nine curriculum modules: networking fundamentals, transport, web, security, network services, file/email, routing, SOC and penetration testing.
- OSI visual, TCP handshake/close, DHCP DORA, DNS, HTTP and TLS flow diagrams.
- Searchable protocol/port explorer.
- Educational packet simulator (does not transmit packets).
- **16,000-question practice bank:** 4,000 questions at each of Beginner, Intermediate, Advanced and Expert.
- Quiz arena supports topic/difficulty filters and question counts up to 4,000 per attempt.
- Questions are generated from a reviewed set of technical facts with scenario-framed variations. They are practice material; verify standards-level details against the linked RFCs.
- Custom question creation and deletion, detailed answer feedback and saved quiz attempts.
- Guided Wireshark, DNS, TLS, DHCP, ARP, localhost Nmap and firewall-log labs.
- SQLAlchemy persistence with SQLite fallback or PostgreSQL.
- Optional OpenAI tutor; offline fallback works without a key.

## Windows / VS Code installation
Install Python 3.11+ and Git. Open this folder in VS Code, then in PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt: `.venv\\Scripts\\activate.bat`. The first run creates `netviz.db` and seeds modules and questions.

## Database
SQLite is the default and requires no setup. For PostgreSQL, create a database (for example at https://neon.tech/) and set:

```powershell
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require"
streamlit run app.py
```

On Streamlit Community Cloud, add `DATABASE_URL` under App → Settings → Secrets. The SQLAlchemy models initialise tables automatically. `schema.sql` is a reference DDL.

## Optional AI tutor
Create a key at https://platform.openai.com/api-keys and set:

```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4.1-mini"
streamlit run app.py
```

Or add these values to Streamlit Secrets. API usage may incur charges. Never commit API keys or database passwords. With no key, the app uses an offline fallback.

## GitHub
Create an empty repository at https://github.com/new, then:

```powershell
git init
git add .
git commit -m "Build NetViz learning platform"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/NetViz.git
git push -u origin main
```

If the remote already has a README you need to keep, run `git pull --rebase origin main` before pushing and resolve any conflicts.

## Streamlit Community Cloud
1. Push this folder to GitHub.
2. Visit https://share.streamlit.io/ and select **New app**.
3. Choose the repository, branch and main file `app.py`.
4. Deploy.
5. Add `DATABASE_URL` and optional `OPENAI_API_KEY` in app Secrets.
6. Reboot after changing secrets.

Docs: https://docs.streamlit.io/deploy/streamlit-community-cloud

## Project layout
`app.py` · `auth.py` · `database.py` · `models.py` · `content.py` · `data/question_bank.json` · `generate_question_bank.py` · `schema.sql` · `components/` · `tests/` · `.streamlit/`

## Security note
The demo registration flow hashes passwords with PBKDF2-HMAC-SHA256 and does not store plaintext passwords. It does not include email verification, password reset, MFA, account lockout or a full production identity provider. Before exposing the app publicly, use a managed authentication service, HTTPS, rate limiting and backups. See the [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

## Testing
```powershell
python -m compileall .
python -m pytest
```

## Troubleshooting
- `streamlit` not recognised: activate `.venv`, then use `python -m streamlit run app.py`.
- Missing dependency: activate `.venv`, run `pip install -r requirements.txt`.
- Database error: verify `DATABASE_URL`, credentials, SSL and network access; unset it to use SQLite.
- AI fallback: set `OPENAI_API_KEY` and restart; verify account limits and model access.
- Port conflict: `python -m streamlit run app.py --server.port 8502`.

## Scope and limitations
This is a learning-project LMS starter with basic local registration/login, guest sessions, learner-specific quiz history, points and leaderboards. It is not a production identity platform: email verification, password reset, MFA, role-based administration, moderation and rate limiting are not included. It does not provide live packet capture or real-time scanning. AI output should be checked against primary standards.

## Reputable references
IETF: https://www.rfc-editor.org/ · Python: https://docs.python.org/3/ · PostgreSQL: https://www.postgresql.org/docs/ · Wireshark: https://www.wireshark.org/docs/ · Scapy: https://scapy.readthedocs.io/ · Nmap: https://nmap.org/book/man.html · OWASP: https://owasp.org/www-project-top-ten/ · MITRE ATT&CK: https://attack.mitre.org/ · OpenAI: https://platform.openai.com/docs/ · Streamlit: https://docs.streamlit.io/


## Accounts, guest mode and rewards
- Register with a username, email and password (10+ characters), or log in.
- Guest mode creates a temporary learner identity for the current browser session. Guest history is not guaranteed to follow the learner to another browser/device.
- Correct answers earn 10 points; a perfect quiz earns a 5-point bonus.
- Badge tiers: 🌱 Newcomer, 🔎 Packet Explorer, ⚡ Protocol Pro, 🛡️ SOC Defender and 🏆 Network Guardian.
- Leaderboards show top learners by points and most quizzes attended.
- For a public production deployment, use HTTPS, managed authentication/email verification, rate limiting, backups and a managed PostgreSQL database. The bundled local authentication is a learning-project implementation, not a substitute for a security-reviewed identity provider.

## Question-bank quality note
The bundled bank contains 16,000 unique question instances (4,000 per difficulty). These are scenario-framed variants built around 50 core knowledge targets per difficulty. The count should not be interpreted as 16,000 independently authored concepts or fully distinct exam-grade scenarios. Review and expand the underlying knowledge targets before using the bank for formal assessment.
