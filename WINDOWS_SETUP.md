# Windows + VS Code
1. Install Python 3.11+ and Git.
2. Extract the ZIP and open the `NetViz` folder in VS Code.
3. Open Terminal → New Terminal and run:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m compileall .
streamlit run app.py
```
Choose the `.venv` interpreter via Ctrl+Shift+P → Python: Select Interpreter.
