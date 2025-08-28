from src.api.schemas.user import UserCreate


def test_schema_user_create():
    obj = UserCreate(username="abc", password="xyz", email="abc@example.com", cpf="12345678901")
    assert obj.username == "abc"
    assert obj.email == "abc@example.com"
    assert obj.password == "xyz"
    assert obj.cpf == "12345678901"