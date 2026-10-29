"""TASK-003/013 / REQ-020: explicit dotenv loading without shell execution/interpolation."""
import os
from pathlib import Path
import re

ALLOWED = {'NEBIUS_API_KEY','NEBIUS_BASE_URL','NEBIUS_MODEL','MASKLAB_MODE','MASKLAB_DATA_DIR','MASKLAB_INFERENCE_BUDGET_USD','MASKLAB_APPROVED_SPEND_USD','MASKLAB_CAPABILITIES_FILE','MASKLAB_OWNER_TOKEN','MASKLAB_MAX_REQUESTS','MASKLAB_MAX_CONCURRENCY','MASKLAB_SPEND_LEDGER','MASKLAB_AUTHORIZATION_ID'}


def load_env_file(path, override=True):
    parsed = {}
    for line_no, line in enumerate(Path(path).read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:]
        if '=' not in line:
            raise ValueError(f'Invalid environment assignment on line {line_no}; values omitted')
        name, value = line.split('=', 1)
        name, value = name.strip(), value.strip()
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', name) or name in parsed:
            raise ValueError(f'Invalid/duplicate environment name on line {line_no}; values omitted')
        if value.startswith(('"', "'")):
            if len(value)<2 or value[-1] != value[0]:
                raise ValueError(f'Unclosed environment quote on line {line_no}; values omitted')
            value = value[1:-1]
        else:
            value = re.split(r'\s+#',value,maxsplit=1)[0].rstrip()
        if name in ALLOWED:
            parsed[name] = value
    for name, value in parsed.items():
        if override or name not in os.environ:
            os.environ[name] = value
    return {name:bool(value) for name,value in parsed.items()}
