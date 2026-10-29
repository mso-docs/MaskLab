"""TASK-013 / REQ-020: no shell execution, interpolation, leaks or implicit dotenv loading."""
import os
import pytest
from masklab.runtime import load_env_file


def test_private_env_is_data_not_shell(tmp_path,monkeypatch):
    file=tmp_path/'.env'
    file.write_text('NEBIUS_API_KEY="$(touch /tmp/DO-NOT-EXECUTE)"\nNEBIUS_MODEL=nvidia/Nemotron-3_5-Lightning\nUNRELATED_VARIABLE=ignored\n')
    monkeypatch.delenv('UNRELATED_VARIABLE',raising=False)
    status=load_env_file(file)
    assert status['NEBIUS_API_KEY'] is True and os.environ['NEBIUS_API_KEY']=='$(touch /tmp/DO-NOT-EXECUTE)'
    assert 'UNRELATED_VARIABLE' not in os.environ
    monkeypatch.delenv('NEBIUS_API_KEY');monkeypatch.delenv('NEBIUS_MODEL')


def test_env_errors_do_not_echo_values(tmp_path):
    file=tmp_path/'.env';file.write_text('NEBIUS_API_KEY="secret-canary\n')
    with pytest.raises(ValueError) as error:load_env_file(file)
    assert 'secret-canary' not in str(error.value)
