from services import audit_service
from data import db




def test_audit_log_insert(test_db):
    conn = test_db
    audit_service.log_audit(conn_or_none=conn, entity_type='test', action='insert', details='unit test')


    cur = conn.execute("SELECT * FROM audit_logs WHERE entity_type = ? ORDER BY id DESC LIMIT 1", ('test',))
    row = cur.fetchone()
    assert row is not None
    assert row['action'] == 'insert'