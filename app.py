import uuid
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File,Form, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
import models
import processor
import solana_env

UPLOAD_DIR = Path("static/audio/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    models.init_db()
    # seed_initial_demo_records()
    yield

app = FastAPI(lifespan=app_lifespan)
solana_client = solana_env.SolanaClient(live=False)

app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

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
        # 1. Execute slow text extraction via Google AI
        extracted_data = processor.process_raw_text(raw_transcript)
        
        # 2. Persist metrics directly into local database entities
        project = db.query(models.CommunityProject).filter(models.CommunityProject.id == project_id).first()
        if project:
            project.title = extracted_data.title
            project.funding_goal = extracted_data.estimated_cost_usd
            project.climate_vulnerability = extracted_data.urgency_rating
            db.commit()
            print(f"🔥 [Async System] Updated project row {project_id} successfully.")

            # 3. Handle secondary asset generations like acoustic ElevenLabs feedback files
            # integrations.generate_voice_broadcast_with_elevenlabs(
            #     f"Ecosystem Status: New urgent project verified. Objective: {extracted_data.title}"
            # )
    except Exception as error:
        print(f"❌ Critical Background Worker system failure: {error}")
    finally:
        db.close()

@app.get("/")
def serve_client_interface(background_tasks: BackgroundTasks):
    # background_tasks.add_task(asynchronous_worker_thread, "123", "Listen, the storm surge yesterday completely washed out the clean water pipes in the lower river sector. It's a massive crisis. We need about nine hundred and fifty bucks for new heavy-duty valves.")
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
        live_balance_sol = solana_env.get_onchain_balance(project.solana_ref)
        project.funding_raised = live_balance_sol * 20.0
        db.commit()

        project_data = {
            "id": project.id,
            "title": project.title,
            "organization": project.organization,
            "funding_goal": project.funding_goal,
            "funding_raised": project.funding_raised,
            "solana_wallet": project.solana_wallet,
            "solana_safe_pda": project.solana_safe_pda or "Devnet_Vault_Active",
            "geohash": project.geohash,
            "created_at": str(project.created_at)
        }
        response_payload.append({"project": project_data, "score": project.calculate_priority_score()})
        
    response_payload.sort(key=lambda x: x["score"], reverse=True)
    return response_payload

@app.post("/api/voice-intake")
def handle_voice_submission(background_tasks: BackgroundTasks, raw_transcript: Optional[str] = Form(None),audio_file: Optional[UploadFile] = File(None), db: Session = Depends(get_db)):
    project_id = f"proj_{uuid.uuid4().hex[:6]}"
    print(raw_transcript)
    # blockchain_identity = solana_env.generate_new_field_wallet()
    blockchain_identity = "123"
    placeholder = models.CommunityProject(
        id=project_id,
        title="Processing Incoming Voice Assets...",
        organization="On-Ground Youth Collective",
        funding_goal=10.0,
        solana_ref=blockchain_identity,
        climate_vulnerability=0.5,
        systemic_marginalization=0.85,
        geographic_isolation=0.70,
        is_youth_led=True,
        status="INIT"
    )
    db.add(placeholder)
    db.commit()

    background_tasks.add_task(asynchronous_worker_thread, project_id, raw_transcript)

    return {"id": project_id, "title": placeholder.title, "solana_wallet": placeholder.solana_ref}

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