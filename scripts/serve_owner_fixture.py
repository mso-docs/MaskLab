"""TASK-012 / REQ-024: isolated browser-only owner workspace; no dotenv/live setup."""
from pathlib import Path
import tempfile
import uvicorn
from masklab.api import create_app

Path('artifacts').mkdir(exist_ok=True)
folder=Path(tempfile.mkdtemp(prefix='owner-e2e-',dir='artifacts'))
# Preserve this run's files for diagnosis, but never reuse an earlier run's jobs/data.
app=create_app(folder,mode='owner')
uvicorn.run(app,host='127.0.0.1',port=8765,access_log=False)
