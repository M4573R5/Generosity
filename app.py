# main.py
import uuid
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session



import models
import processor

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    print("🚀 Booting up API core infrastructure systems...")
    models.init_db()
    seed_initial_demo_records()
    yield

app = FastAPI(lifespan=app_lifespan)

# Allow Cross-Origin Resource Sharing (CORS) for decoupled client connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def asynchronous_worker_thread(project_id: str, raw_transcript: str):
    """Executes heavy AI parsing calls out-of-band without locking main UI requests."""
    db = models.SessionLocal()
    try:
        pass
    except Exception as error:
        print(f"❌ Critical Background Worker system failure: {error}")
    finally:
        db.close()

@app.get("/")
def serve_client_interface():
    processor.process_raw_text("Listen, the storm surge yesterday completely washed out the clean water pipes in the lower river sector. It's a massive crisis. We need about nine hundred and fifty bucks for new heavy-duty valves.")
    return FileResponse("templates/index.html")


def seed_initial_demo_records():
    db = models.SessionLocal()
    if db.query(models.CommunityProject).count() == 0:
        p = models.CommunityProject(
            id="proj_seed_initial", title="Mangrove Resilience Buffer Layout", organization="Coastal Youth Action",
            funding_goal=2500.0, funding_raised=450.0, solana_wallet="9xK3pG7Xm4...Kvd",
            climate_vulnerability=0.95, systemic_marginalization=0.82, geographic_isolation=0.75, is_youth_led=True
        )
        db.add(p)
        db.commit()
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)