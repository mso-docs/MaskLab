"""TASK-014 / REQ-025: local static QA only."""
import http.server
from pathlib import Path
import functools
root=Path(__file__).resolve().parents[2]/'artifacts/release/pages'
server=http.server.ThreadingHTTPServer(('127.0.0.1',8770),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
print('Static preview: http://127.0.0.1:8770',flush=True)
server.serve_forever()
