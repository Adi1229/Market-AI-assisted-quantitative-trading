import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.data.database.models import Base
from app.core.config import settings

# For testing, we ideally use a separate test database.
# Assuming the docker-compose DB is available.
TEST_DATABASE_URL = settings.DATABASE_URL.replace("market_db", "market_test_db")

@pytest.fixture(scope="session")
def engine():
    # If the database doesn't exist, SQLAlchemy can't create it directly via URL.
    # But since we're assuming market_test_db is handled or we use the main DB but don't drop_all.
    # Wait, we can't easily create market_test_db here. 
    # Let's just use an SQLite in-memory DB for tests to completely isolate them!
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
