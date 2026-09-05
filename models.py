from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
ENGINE = create_engine("sqlite:///impact_hub.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

class CommunityProject(Base):
    __tablename__ = "community_projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    funding_goal = Column(Float, nullable=False)
    funding_raised = Column(Float, default=0.0)
    solana_ref = Column(String, nullable=False)
    solana_safe_pda = Column(String, nullable=True) 
    geohash = Column(String, nullable=True) 
    climate_vulnerability = Column(Float, default=0.0)
    systemic_marginalization = Column(Float, default=0.0)
    geographic_isolation = Column(Float, default=0.0)
    is_youth_led = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=True) 
    ledgers = relationship("AuditLedger", back_populates="project")

    def calculate_priority_score(self) -> float:
        CLIMATE_W = 0.45
        EQUITY_W = 0.35
        GEOGRAPHY_W = 0.20

        raw_score = (
            (self.climate_vulnerability * CLIMATE_W) +
            (self.systemic_marginalization * EQUITY_W) +
            (self.geographic_isolation * GEOGRAPHY_W)
        )
        multiplier = 1.15 if self.is_youth_led else 1.0
        return round(raw_score * multiplier, 4)

class AuditLedger(Base):
    __tablename__ = "audit_ledgers"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("community_projects.id"))
    amount_spent = Column(Float, nullable=False)
    category = Column(String, nullable=False) 
    proof_description = Column(String, nullable=False)
    solana_signature = Column(String, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    project = relationship("CommunityProject", back_populates="ledgers")

def init_db():
    Base.metadata.create_all(bind=ENGINE)
