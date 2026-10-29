"""TASK-013 / REQ-021: shared cumulative grants; no paid calls."""
from concurrent.futures import ThreadPoolExecutor
import pytest
from masklab.budget import SpendLedger


def test_shared_atomic_reservations_and_restarts(tmp_path):
    path=tmp_path/'ledger.sqlite3';ledger=SpendLedger.initialize(path,'explicit-user-grant','1')
    def reserve(i):
        try:SpendLedger(path,'explicit-user-grant').reserve(str(i),str(i),'q','0.4');return True
        except ValueError:return False
    with ThreadPoolExecutor(max_workers=8) as pool:assert sum(pool.map(reserve,range(8)))==2
    assert ledger.snapshot()['held_usd']=='0.8'
    assert SpendLedger(path,'explicit-user-grant').snapshot()['remaining_usd']=='0.2'
    with pytest.raises(ValueError):SpendLedger.initialize(path,'new-authorization','10')
    with pytest.raises(ValueError):SpendLedger.initialize(path,'explicit-user-grant','10')


def test_unknown_usage_halts_all_workspaces_without_expiry(tmp_path):
    ledger=SpendLedger.initialize(tmp_path/'ledger.sqlite3','grant','10')
    ledger.reserve('a','workspace-1','q','0.1')
    ledger.settle('a',uncertain=True)
    assert ledger.snapshot()['held_usd']=='0.1'
    with pytest.raises(ValueError,match='HALTED'):ledger.reserve('b','workspace-2','q','0.1')


def test_settlement_idempotency_and_violation(tmp_path):
    ledger=SpendLedger.initialize(tmp_path/'ledger.sqlite3','grant','10')
    ledger.reserve('a','one','q','0.1');ledger.settle('a','0.01');ledger.settle('a','0.01')
    assert ledger.snapshot()['remaining_usd']=='9.99'
    with pytest.raises(ValueError):ledger.settle('a','0.02')
    ledger.reserve('b','two','q','0.1');ledger.settle('b','0.2')
    assert ledger.snapshot()['halted']=='RESERVATION_EXCEEDED'


def test_cross_database_crash_window_is_conservative(tmp_path):
    ledger=SpendLedger.initialize(tmp_path/'ledger.sqlite3','grant','10')
    ledger.reserve('before-intent','one','q','0.1');ledger.recover_workspace('one',{})
    assert ledger.snapshot()['uncertain_attempts']==1
    second=SpendLedger.initialize(tmp_path/'second.sqlite3','grant','10')
    second.reserve('after-local-commit','one','q','0.1')
    second.recover_workspace('one',{'after-local-commit':{'cost_state':'KNOWN','cost_usd':'0.02'}})
    assert second.snapshot()['estimated_spent_usd']=='0.02'


def test_no_missing_ledger_reset(tmp_path):
    with pytest.raises(ValueError,match='missing'):SpendLedger(tmp_path/'absent.sqlite3','grant')


def test_restoring_or_copying_old_workspace_cannot_replay_attempt(tmp_path):
    ledger=SpendLedger.initialize(tmp_path/'ledger.sqlite3','grant','10')
    ledger.reserve('first','original-path','globally-unique-request','0.1',ordinal=1)
    ledger.settle('first','0.02')
    with pytest.raises(ValueError,match='HISTORY_MISMATCH'):
        ledger.reserve('replayed','restored-new-path','globally-unique-request','0.1',ordinal=1)
    ledger.reserve('documented-second-attempt','restored-new-path','globally-unique-request','0.1',ordinal=2)
    assert ledger.snapshot()['attempts']==2
