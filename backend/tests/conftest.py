import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.data.database.models import Base
from app.core.config import settings

# For testing, we ideally use a separate test database.
# Assuming the docker-compose DB is available.
TEST_DATABASE_URL = settings.DATABASE_URL.replace("market_db", "market_db")

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
