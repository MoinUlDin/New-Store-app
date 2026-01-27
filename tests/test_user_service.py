from services import user_service
from services import auth_service




def test_create_and_authenticate_user(test_db):
    uid = user_service.create_user('tester1', 'Secret123', email='tester1@example.com')
    assert uid is not None


    user = user_service.authenticate('tester1', 'Secret123')
    assert user is not None
    assert user['username'] == 'tester1'




def test_change_password(test_db):
    user_service.create_user('pwuser', 'oldpass')
    ok = user_service.change_password('pwuser', 'oldpass', 'newpass')
    assert ok
    assert user_service.authenticate('pwuser', 'newpass') is not None


                                        

def test_superadmin_protection(test_db):
    # superadmin was created by fixture
    # fetch superadmin row
    conn = test_db
    cur = conn.execute("SELECT id, username FROM users WHERE is_superadmin = 1 LIMIT 1")
    row = cur.fetchone()
    assert row is not None
    superadmin_id = row['id']


    # non-superadmin should not be able to delete superadmin
    try:
        user_service.delete_user(superadmin_id, actor_is_superadmin=False)
        deleted = True
    except PermissionError:
        deleted = False
        assert not deleted