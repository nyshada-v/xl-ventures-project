from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import uuid
from backend.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Company(Base):
    __tablename__ = "companies"
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name          = Column(String, nullable=False)
    domain        = Column(String, unique=True)
    industry      = Column(String)
    headcount     = Column(Integer)
    funding_stage = Column(String)
    country       = Column(String)
    description   = Column(Text)
    icp_score     = Column(Float)
    trigger       = Column(String)
    raw_data      = Column(JSON)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Contact(Base):
    __tablename__ = "contacts"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id  = Column(String)
    name        = Column(String)
    title       = Column(String)
    email       = Column(String)
    phone       = Column(String)
    linkedin    = Column(String)
    seniority   = Column(String)
    raw_data    = Column(JSON)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status      = Column(String, default="pending")
    plan        = Column(JSON)
    results     = Column(JSON)
    error       = Column(Text)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))

class HitlDecision(Base):
    __tablename__ = "hitl_decisions"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id      = Column(String)
    company_id  = Column(String)
    decision    = Column(String)
    notes       = Column(Text)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SentEmail(Base):
    __tablename__ = "sent_emails"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id  = Column(String)
    contact_email = Column(String)
    contact_name  = Column(String)
    subject     = Column(Text)
    body        = Column(Text)
    status      = Column(String, default="sent")  # sent / failed
    error       = Column(Text)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def init_db():
    Base.metadata.create_all(bind=engine)