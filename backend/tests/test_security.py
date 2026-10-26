from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_cannot_be_used_as_the_original_password() -> None:
    password_hash = hash_password("a-safe-test-password")

    assert password_hash != "a-safe-test-password"
    assert verify_password("a-safe-test-password", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_access_token_is_signed() -> None:
    token = create_access_token("42")

    assert token.count(".") == 2
