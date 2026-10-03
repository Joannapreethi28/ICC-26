from mak.records.reconcile import reconcile


def test_missing_database_is_flagged_instead_of_reported_as_a_match(tmp_path):
    rows = reconcile(db_path=tmp_path / 'absent.duckdb')
    assert len(rows) == 26
    assert all(r['status'] == 'flagged' and r['computed_value'] is None and r['reason'] for r in rows)
    assert all(r['golden_as_of'] for r in rows)
