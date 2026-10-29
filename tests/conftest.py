import pytest
from masklab.api import sample_dataset
from masklab.contracts import ProtocolConfig, render_protocol, digest
from masklab.store import Store

@pytest.fixture
def store(tmp_path):
    return Store(tmp_path/'workspace.sqlite3')

@pytest.fixture
def dataset():
    return sample_dataset()

@pytest.fixture
def make_run(store,dataset):
    def make(scenario='success', repetitions=1, questions=2, **kwargs):
        data = dataset.model_copy(deep=True)
        data.questions = data.questions[:questions]
        cfg = ProtocolConfig(simulation_scenario=scenario,repetitions=repetitions,**kwargs)
        s = store.create_study('Test study')
        store.add_dataset(s['id'],data.model_dump(),b'original source')
        p = store.freeze(s['id'],render_protocol(data,cfg,digest(b'original source')))
        return store.create_run(p['id'],'test-key-'+p['id']),p['protocol']
    return make


@pytest.fixture(autouse=True)
def isolated_spend_ledger(tmp_path,monkeypatch):
    from masklab.budget import SpendLedger
    path=tmp_path/'shared-budget.sqlite3'
    SpendLedger.initialize(path,'test-only-authorization','10')
    monkeypatch.setenv('MASKLAB_SPEND_LEDGER',str(path))
    monkeypatch.setenv('MASKLAB_AUTHORIZATION_ID','test-only-authorization')
