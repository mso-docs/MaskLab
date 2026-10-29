"""TASK-012 / TEST-023: invoke from /tmp with the fresh installed-wheel Python."""
import importlib.resources as resources
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from masklab.api import sample_dataset,create_app
assert len(sample_dataset().questions)==24
assert resources.files('masklab').joinpath('static/brand/masklab-logo.svg').is_file()
with TemporaryDirectory(prefix='masklab-wheel-') as folder:
    with TestClient(create_app(folder,embedded_worker=False)) as client:
        assert client.get('/').status_code==200
        assert client.get('/brand/masklab-logo.svg').headers['content-type'].startswith('image/svg+xml')
print('PASS: installed wheel outside source tree serves React, brand assets and fixture dataset')
