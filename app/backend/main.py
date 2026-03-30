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


@app.get("/export/pdf/{transcript_id}")
def export_pdf(transcript_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from fastapi.responses import StreamingResponse
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    transcript = db.query(Transcript).filter(
        Transcript.id == transcript_id,
        Transcript.user_id == user.id
    ).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    courses = db.query(CourseRecord).filter(CourseRecord.transcript_id == transcript_id).all()
    audit = db.query(AuditResult).filter(AuditResult.transcript_id == transcript_id).first()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=18, spaceAfter=6, textColor=colors.HexColor('#1a365d'))
    heading_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=13, spaceAfter=4, spaceBefore=12, textColor=colors.HexColor('#2b6cb0'))
    normal_style = ParagraphStyle('Body2', parent=styles['Normal'], fontSize=10, spaceAfter=3)
    small_style = ParagraphStyle('Small2', parent=styles['Normal'], fontSize=8, textColor=colors.grey)

    elements = []

    elements.append(Paragraph("NSU Academic Audit Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y')} | Confidential Student Record", small_style))
    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a365d')))
    elements.append(Spacer(1, 4*mm))

    if audit:
        elements.append(Paragraph("Student Information", heading_style))
        info_data = [
            ["Email:", user.email or "N/A"],
            ["Program:", audit.program or "N/A"],
            ["Major:", audit.major or "Not Detected"],
            ["CGPA:", f"{audit.cgpa:.2f}"],
            ["Academic Standing:", audit.academic_standing or "N/A"],
        ]
        info_table = Table(info_data, colWidths=[50*mm, 100*mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 4*mm))

        elements.append(Paragraph("Credit Summary", heading_style))
        credit_data = [
            ["Credits Earned:", f"{audit.credits_earned:.1f}"],
            ["Credits Attempted:", f"{audit.credits_attempted:.1f}"],
            ["Failed Credits:", f"{audit.failed_credits:.1f}"],
            ["Withdrawn Credits:", f"{audit.withdrawn_credits:.1f}"],
            ["Total Required:", f"{audit.total_required}"],
            ["Credits Remaining:", f"{audit.credits_remaining:.1f}"],
            ["Progress:", f"{audit.progress_percent:.1f}%"],
            ["Est. Semesters Left:", f"{audit.estimated_semesters}"],
        ]
        credit_table = Table(credit_data, colWidths=[50*mm, 100*mm])
        credit_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(credit_table)
        elements.append(Spacer(1, 4*mm))

        if audit.category_progress:
            elements.append(Paragraph("Program Requirement Progress", heading_style))
            cat_data = [["Category", "Completed", "Required", "Percent"]]
            for cat_name, cat_info in audit.category_progress.items():
                cat_data.append([
                    cat_name,
                    f"{cat_info.get('completed', 0):.1f}",
                    f"{cat_info.get('required', 0)}",
                    f"{cat_info.get('percent', 0):.1f}%"
                ])
            cat_table = Table(cat_data, colWidths=[55*mm, 30*mm, 30*mm, 30*mm])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(cat_table)
            elements.append(Spacer(1, 4*mm))

        if audit.waiver_status:
            elements.append(Paragraph("Waiver Status", heading_style))
            waiver_data = [["Course", "Status"]]
            for wc, ws in audit.waiver_status.items():
                waiver_data.append([wc, ws])
            waiver_table = Table(waiver_data, colWidths=[60*mm, 90*mm])
            waiver_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(waiver_table)
            elements.append(Spacer(1, 4*mm))

    if courses:
        elements.append(Spacer(1, 4*mm))
        elements.append(Paragraph("Transcript Courses", heading_style))
        course_data = [["Code", "Title", "Credits", "Grade", "Valid"]]
        for c in courses:
            course_data.append([
                c.course_code,
                c.course_title or "N/A",
                f"{c.credits:.1f}",
                c.grade or "N/A",
                "Yes" if c.is_valid_nsu else "No"
            ])
        course_table = Table(course_data, colWidths=[30*mm, 60*mm, 20*mm, 20*mm, 20*mm])
        course_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(course_table)

    if audit and audit.missing_courses:
        elements.append(Spacer(1, 4*mm))
        elements.append(Paragraph(f"Missing Required Courses ({len(audit.missing_courses)})", heading_style))
        for i in range(0, len(audit.missing_courses), 3):
            row = audit.missing_courses[i:i+3]
            while len(row) < 3:
                row.append("")
            elements.append(Paragraph("  |  ".join(row), normal_style))

    if audit and audit.invalid_courses:
        elements.append(Spacer(1, 4*mm))
        elements.append(Paragraph("Invalid Courses Detected", heading_style))
        for ic in audit.invalid_courses:
            if isinstance(ic, dict):
                elements.append(Paragraph(f"  - {ic.get('course_code', 'Unknown')} ({ic.get('course_title', '')}) - {ic.get('credits', 0):.1f} cr - Grade: {ic.get('grade', 'N/A')}", normal_style))

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Paragraph("This report was generated by NSU Academic Audit System. For official records, please contact the university registrar.", small_style))

    doc.build(elements)
    buffer.seek(0)

    filename = f"NSU_Audit_Report_{transcript_id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
