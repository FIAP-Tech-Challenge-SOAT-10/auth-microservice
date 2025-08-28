from app.schemas.user import UserCreate


def test_schema_user_create():
    obj = UserCreate(username="abc", password="xyz", email="abc@example.com")
    assert obj.username == "abc"
    assert obj.email == "abc@example.com"
    assert obj.password == "xyz"
