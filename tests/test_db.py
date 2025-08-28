from src.infrastructure.database.session import engine


def test_engine_exists():
    assert engine is not None
