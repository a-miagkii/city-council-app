import pytest

from models import User


def test_user_password_hashing(session):
    user = User(email="user@example.com")
    user.set_password("secret123")

    session.add(user)
    session.commit()

    assert user.password_hash != "secret123"
    assert user.check_password("secret123") is True
    assert user.check_password("wrong") is False


def test_user_email_validation(session):
    with pytest.raises(AssertionError):
        User(email="bad-email")
