from auth import hash_password, verify_password

def test_password_hash_roundtrip():
    encoded=hash_password("sample-long-password")
    assert verify_password("sample-long-password",encoded)
    assert not verify_password("wrong-password",encoded)
