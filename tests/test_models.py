from app.models.user import User


def test_user_model_fields():
    user = User(username="test", password_hash="123")
    assert getattr(user, "username") == "test"
    assert hasattr(user, "id")
