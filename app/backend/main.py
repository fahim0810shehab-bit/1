import os
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import User, Transcript, CourseRecord, AuditResult, History
from auth import create_access_token, verify_token
from parser import parse_transcript, detect_file_type
from audit_engine import run_audit, CATALOG

app = FastAPI(title="NSU Academic Audit API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 1 * 1024 * 1024


@app.on_event("startup")
def startup():
    init_db()


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("email")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/")
def root():
    return {"message": "NSU Academic Audit API", "version": "1.0.0"}


@app.post("/auth/google")
def google_login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    name = data.get("name", "")
    picture = data.get("picture", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, picture=picture, provider="google")
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.name = name
        user.picture = picture
        user.last_login = datetime.utcnow()
        db.commit()

    token = create_access_token({"email": user.email, "user_id": user.id})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    }


@app.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture
    }


@app.post("/transcripts/upload")
async def upload_transcript(
    file: UploadFile = File(...),
    level: int = 3,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 1MB)")

    file_type = detect_file_type(file.filename or "")
    if file_type == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV, PDF, or image.")

    courses_data = parse_transcript(content, file.filename or "unknown")

    transcript = Transcript(
        user_id=user.id,
        filename=file.filename,
        file_type=file_type,
        level_used=level,
        raw_data=courses_data
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    for c in courses_data:
        record = CourseRecord(
            transcript_id=transcript.id,
            course_code=c.get("course_code", ""),
            course_title=c.get("course_title", ""),
            credits=c.get("credits", 0.0),
            grade=c.get("grade", ""),
            semester=c.get("semester", ""),
            year=c.get("year"),
            attempt=c.get("attempt", 1),
            is_valid_nsu=c.get("is_valid_nsu", 0)
        )
        db.add(record)
    db.commit()

    result = run_audit(courses_data, level)

    audit = AuditResult(
        transcript_id=transcript.id,
        cgpa=result["cgpa"],
        total_quality_points=result["total_quality_points"],
        credits_attempted=result["credits_attempted"],
        credits_earned=result["credits_earned"],
        failed_credits=result["failed_credits"],
        withdrawn_credits=result["withdrawn_credits"],
        incomplete_credits=result["incomplete_credits"],
        academic_standing=result["academic_standing"],
        program=result["program"],
        major=result["major"],
        total_required=result["total_required"],
        credits_remaining=result["credits_remaining"],
        progress_percent=result["progress_percent"],
        estimated_semesters=result["estimated_semesters"],
        waiver_status=result["waiver_status"],
        missing_courses=result["missing_courses"],
        category_progress=result["category_progress"],
        invalid_courses=result["invalid_courses"],
        retake_history=result["retake_history"],
        result_data=result
    )
    db.add(audit)

    transcript.program_detected = result["program"]

    history_entry = History(
        user_id=user.id,
        transcript_id=transcript.id,
        action="audit",
        filename=file.filename,
        program=result["program"],
        level_used=level,
        cgpa=result["cgpa"]
    )
    db.add(history_entry)
    db.commit()

    return {
        "transcript_id": transcript.id,
        "result": result
    }


@app.post("/audit/run")
def run_audit_on_transcript(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transcript_id = data.get("transcript_id")
    level = data.get("level", 3)

    transcript = db.query(Transcript).filter(
        Transcript.id == transcript_id,
        Transcript.user_id == user.id
    ).first()

    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    courses_data = transcript.raw_data or []
    result = run_audit(courses_data, level)

    existing = db.query(AuditResult).filter(AuditResult.transcript_id == transcript_id).first()
    if existing:
        existing.cgpa = result["cgpa"]
        existing.total_quality_points = result["total_quality_points"]
        existing.credits_attempted = result["credits_attempted"]
        existing.credits_earned = result["credits_earned"]
        existing.failed_credits = result["failed_credits"]
        existing.withdrawn_credits = result["withdrawn_credits"]
        existing.incomplete_credits = result["incomplete_credits"]
        existing.academic_standing = result["academic_standing"]
        existing.program = result["program"]
        existing.major = result["major"]
        existing.total_required = result["total_required"]
        existing.credits_remaining = result["credits_remaining"]
        existing.progress_percent = result["progress_percent"]
        existing.estimated_semesters = result["estimated_semesters"]
        existing.waiver_status = result["waiver_status"]
        existing.missing_courses = result["missing_courses"]
        existing.category_progress = result["category_progress"]
        existing.invalid_courses = result["invalid_courses"]
        existing.retake_history = result["retake_history"]
        existing.result_data = result
        existing.computed_at = datetime.utcnow()
    else:
        audit = AuditResult(
            transcript_id=transcript_id,
            cgpa=result["cgpa"],
            total_quality_points=result["total_quality_points"],
            credits_attempted=result["credits_attempted"],
            credits_earned=result["credits_earned"],
            failed_credits=result["failed_credits"],
            withdrawn_credits=result["withdrawn_credits"],
            incomplete_credits=result["incomplete_credits"],
            academic_standing=result["academic_standing"],
            program=result["program"],
            major=result["major"],
            total_required=result["total_required"],
            credits_remaining=result["credits_remaining"],
            progress_percent=result["progress_percent"],
            estimated_semesters=result["estimated_semesters"],
            waiver_status=result["waiver_status"],
            missing_courses=result["missing_courses"],
            category_progress=result["category_progress"],
            invalid_courses=result["invalid_courses"],
            retake_history=result["retake_history"],
            result_data=result
        )
        db.add(audit)

    transcript.level_used = level
    db.commit()

    return {"result": result}


@app.get("/transcripts")
def list_transcripts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transcripts = db.query(Transcript).filter(Transcript.user_id == user.id).order_by(Transcript.uploaded_at.desc()).all()
    result = []
    for t in transcripts:
        audit = db.query(AuditResult).filter(AuditResult.transcript_id == t.id).first()
        result.append({
            "id": t.id,
            "filename": t.filename,
            "file_type": t.file_type,
            "program_detected": t.program_detected,
            "level_used": t.level_used,
            "uploaded_at": t.uploaded_at.isoformat() if t.uploaded_at else None,
            "cgpa": audit.cgpa if audit else None,
            "academic_standing": audit.academic_standing if audit else None
        })
    return result


@app.get("/transcripts/{transcript_id}")
def get_transcript(transcript_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transcript = db.query(Transcript).filter(
        Transcript.id == transcript_id,
        Transcript.user_id == user.id
    ).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    courses = db.query(CourseRecord).filter(CourseRecord.transcript_id == transcript_id).all()
    audit = db.query(AuditResult).filter(AuditResult.transcript_id == transcript_id).first()

    return {
        "id": transcript.id,
        "filename": transcript.filename,
        "file_type": transcript.file_type,
        "program_detected": transcript.program_detected,
        "level_used": transcript.level_used,
        "uploaded_at": transcript.uploaded_at.isoformat() if transcript.uploaded_at else None,
        "courses": [{
            "course_code": c.course_code,
            "course_title": c.course_title,
            "credits": c.credits,
            "grade": c.grade,
            "semester": c.semester,
            "year": c.year,
            "attempt": c.attempt,
            "is_valid_nsu": c.is_valid_nsu
        } for c in courses],
        "audit_result": audit.result_data if audit else None
    }


@app.get("/history")
def get_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.query(History).filter(History.user_id == user.id).order_by(History.timestamp.desc()).all()
    return [{
        "id": h.id,
        "transcript_id": h.transcript_id,
        "action": h.action,
        "filename": h.filename,
        "program": h.program,
        "level_used": h.level_used,
        "cgpa": h.cgpa,
        "timestamp": h.timestamp.isoformat() if h.timestamp else None
    } for h in entries]


@app.delete("/history/{history_id}")
def delete_history(history_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(History).filter(History.id == history_id, History.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Deleted"}


@app.get("/catalog")
def get_catalog():
    return {
        "courses": CATALOG["courses"],
        "programs": {k: {"name": v["name"], "total_credits": v["total_credits"]} for k, v in CATALOG["programs"].items()}
    }
