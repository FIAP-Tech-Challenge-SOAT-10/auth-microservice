from app.database import engine


def test_engine_exists():
    assert engine is not None
