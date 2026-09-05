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
    background_tasks.add_task(asynchronous_worker_thread, project_id, raw_transcript)

    processor.process_raw_text("Listen, the storm surge yesterday completely washed out the clean water pipes in the lower river sector. It's a massive crisis. We need about nine hundred and fifty bucks for new heavy-duty valves.")
    return FileResponse("templates/index.html")

@app.get("/api/stream-status/{api_token}")
async def server_sent_events_stream_endpoint(api_token: str):
    async def database_event_watcher():
        db = models.SessionLocal()
        try:
            while True:
                project_id = 1 #testing
                yield f"data: Hello world"
                project = db.query(models.CommunityProject).filter(models.CommunityProject.id == project_id).first()
                
        finally:
            db.close()

    return StreamingResponse(database_event_watcher(), media_type="text/event-stream")

@app.get("/api/projects")
def read_prioritized_queue(db: Session = Depends(get_db)):
    all_projects = db.query(models.CommunityProject).all()
    response_payload = []
    
    for project in all_projects:
        project_data = {
            "id": project.id,
            "title": project.title,
            "organization": project.organization,
            "funding_goal": project.funding_goal,
            "funding_raised": project.funding_raised,
            "solana_wallet": project.solana_wallet
        }
        response_payload.append({"project": project_data,"score": project.calculate_priority_score()})

    response_payload.sort(key=lambda x: x["score"], reverse=True)
    return response_payload

@app.post("/api/voice-intake")
def handle_voice_submission(background_tasks: BackgroundTasks,raw_transcript: str = Form(...),db: Session = Depends(get_db)):
    project_id = f"proj_{uuid.uuid4().hex[:6]}"
    placeholder = models.CommunityProject(
        id=project_id,
        title="Processing Incoming Voice Assets...",
        organization="On-Ground Youth Collective",
        funding_goal=100.0,
        solana_wallet="SolanaFieldKey_" + uuid.uuid4().hex[:8],
        climate_vulnerability=0.5,
        systemic_marginalization=0.85,
        geographic_isolation=0.70,
        is_youth_led=True
    )
    db.add(placeholder)
    db.commit()

    # 🚀 THE COMPETITIVE EDGE: Hand the slow AI processing over to background threads out-of-band
    background_tasks.add_task(asynchronous_worker_thread, project_id, raw_transcript)

    # Return immediate JSON confirmation chunk back to vanilla JavaScript fetch call
    return {"id": placeholder.id, "title": placeholder.title, "solana_wallet": placeholder.solana_wallet}

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