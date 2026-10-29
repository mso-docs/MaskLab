"""TASK-010/012: prepare a public derivative without changing private originals."""
from pathlib import Path
from masklab.portable import public_redacted_archive

if __name__ == '__main__':
    source = Path('artifacts/live-verification/matrix.zip')
    original = source.read_bytes()
    target = Path('public-evidence/matrix-redacted.zip')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(public_redacted_archive(original))
    assert source.read_bytes() == original
    print('Prepared public timestamp-redacted evidence; private original preserved. Not published.')
