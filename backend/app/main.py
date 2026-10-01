import os
from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import get_db
from .models import AuditLog, BusinessRecord, EntityRelationship
from .schemas import RecordCreate, RecordRead, RecordUpdate, RelationshipCreate, RelationshipRead, WeightedScoreRequest

app = FastAPI(title="STRATIVA API", version="0.2.0", docs_url="/docs")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5174").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def audit(db: Session, action: str, record: BusinessRecord) -> None:
    db.add(AuditLog(tenant_id=record.tenant_id, action=action, entity_type=record.category, entity_id=str(record.id), payload={"title": record.title, "code": record.code}))

def sync_links(db: Session, record: BusinessRecord, links) -> None:
    db.execute(delete(EntityRelationship).where(EntityRelationship.tenant_id == record.tenant_id, EntityRelationship.source_id == record.id))
    for link in links:
        target = db.get(BusinessRecord, link.target_id)
        if not target or target.deleted_at or target.tenant_id != record.tenant_id:
            raise HTTPException(422, "یکی از ارتباط‌های انتخاب‌شده معتبر نیست")
        db.add(EntityRelationship(tenant_id=record.tenant_id, source_id=record.id, target_id=link.target_id, relationship_type=link.relationship_type))

def validate_business_rules(db: Session, category: str, data: dict, record_id: UUID | None = None) -> None:
    if category == "kpis":
        weight = float(data.get("weight") or 0)
        if weight <= 0 or weight > 100: raise HTTPException(422, "وزن شاخص باید بزرگ‌تر از صفر و حداکثر ۱۰۰ باشد")
    if category == "strategy_maps" and data.get("source_objective_id") == data.get("target_objective_id"):
        raise HTTPException(422, "هدف مبدأ و مقصد در نقشه استراتژی باید متفاوت باشند")
    if category == "frameworks" and data.get("framework_type") == "Custom / Hybrid" and not data.get("custom_method_name"):
        raise HTTPException(422, "برای چارچوب سفارشی، نام روش دلخواه را وارد کنید")
    if category == "risks":
        ip, ii = float(data.get("inherent_probability") or 0), float(data.get("inherent_impact") or 0)
        rp, ri = float(data.get("residual_probability") or 0), float(data.get("residual_impact") or 0)
        if not 1 <= ip <= 5 or not 1 <= ii <= 5: raise HTTPException(422, "احتمال و اثر ذاتی باید بین ۱ تا ۵ باشند")
        if rp and not 1 <= rp <= 5 or ri and not 1 <= ri <= 5: raise HTTPException(422, "احتمال و اثر باقیمانده باید بین ۱ تا ۵ باشند")
        data["inherent_score"] = str(ip * ii)
        if rp and ri: data["residual_score"] = str(rp * ri)
    if category == "processes" and record_id and data.get("parent_process_id"):
        current = data.get("parent_process_id")
        visited = {str(record_id)}
        while current:
            if current in visited: raise HTTPException(422, "انتخاب فرآیند بالادست باعث ایجاد حلقه در درختواره می‌شود")
            visited.add(current)
            parent = db.get(BusinessRecord, UUID(current))
            current = (parent.data or {}).get("parent_process_id") if parent else None

@app.get("/health")
def health(): return {"status": "ok", "service": "strativa-api"}

@app.get("/api/records", response_model=list[RecordRead])
def list_records(category: str = Query(min_length=2), q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(BusinessRecord).where(BusinessRecord.tenant_id == "demo-tenant", BusinessRecord.category == category, BusinessRecord.deleted_at.is_(None)).order_by(BusinessRecord.updated_at.desc())
    if q: stmt = stmt.where(BusinessRecord.title.ilike(f"%{q}%"))
    return db.scalars(stmt).all()

@app.post("/api/records", response_model=RecordRead, status_code=201)
def create_record(payload: RecordCreate, db: Session = Depends(get_db)):
    validate_business_rules(db, payload.category, payload.data)
    record = BusinessRecord(**payload.model_dump(exclude={"links"}), tenant_id="demo-tenant")
    db.add(record)
    try:
        db.flush(); sync_links(db, record, payload.links); audit(db, "create", record); db.commit(); db.refresh(record); return record
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "کد واردشده در این بخش تکراری است")

@app.put("/api/records/{record_id}", response_model=RecordRead)
def update_record(record_id: UUID, payload: RecordUpdate, db: Session = Depends(get_db)):
    record = db.get(BusinessRecord, record_id)
    if not record or record.deleted_at: raise HTTPException(404, "رکورد پیدا نشد")
    validate_business_rules(db, payload.category, payload.data, record_id)
    for key, value in payload.model_dump(exclude={"links"}).items(): setattr(record, key, value)
    try:
        sync_links(db, record, payload.links); audit(db, "update", record); db.commit(); db.refresh(record); return record
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "کد واردشده در این بخش تکراری است")

@app.delete("/api/records/{record_id}", status_code=204)
def delete_record(record_id: UUID, db: Session = Depends(get_db)):
    record = db.get(BusinessRecord, record_id)
    if not record or record.deleted_at: raise HTTPException(404, "رکورد پیدا نشد")
    record.deleted_at = datetime.now(timezone.utc); audit(db, "delete", record); db.commit()

@app.get("/api/relationships/{record_id}", response_model=list[RelationshipRead])
def list_relationships(record_id: UUID, db: Session = Depends(get_db)):
    stmt = select(EntityRelationship).where(EntityRelationship.tenant_id == "demo-tenant", or_(EntityRelationship.source_id == record_id, EntityRelationship.target_id == record_id))
    return db.scalars(stmt).all()

@app.post("/api/relationships", response_model=RelationshipRead, status_code=201)
def create_relationship(payload: RelationshipCreate, db: Session = Depends(get_db)):
    if payload.source_id == payload.target_id: raise HTTPException(422, "یک موجودیت نمی‌تواند به خودش متصل شود")
    source, target = db.get(BusinessRecord, payload.source_id), db.get(BusinessRecord, payload.target_id)
    if not source or not target or source.deleted_at or target.deleted_at: raise HTTPException(404, "یکی از موجودیت‌ها پیدا نشد")
    relation = EntityRelationship(**payload.model_dump(), tenant_id="demo-tenant")
    db.add(relation); db.commit(); db.refresh(relation); return relation

@app.delete("/api/relationships/{relationship_id}", status_code=204)
def delete_relationship(relationship_id: UUID, db: Session = Depends(get_db)):
    relation = db.get(EntityRelationship, relationship_id)
    if not relation: raise HTTPException(404, "رابطه پیدا نشد")
    db.delete(relation); db.commit()

@app.get("/api/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    rows = db.execute(select(BusinessRecord.category, func.count(BusinessRecord.id)).where(BusinessRecord.tenant_id == "demo-tenant", BusinessRecord.deleted_at.is_(None)).group_by(BusinessRecord.category)).all()
    return {"counts": {category: count for category, count in rows}, "total": sum(count for _, count in rows)}

@app.get("/api/analytics/gaps")
def strategic_gaps(db: Session = Depends(get_db)):
    records = db.scalars(select(BusinessRecord).where(BusinessRecord.tenant_id == "demo-tenant", BusinessRecord.deleted_at.is_(None))).all()
    gaps = []
    for record in records:
        data = record.data or {}
        if record.category in {"strategies", "objectives", "kpis", "processes", "risks", "initiatives", "projects"} and not data.get("owner") and not data.get("manager"):
            gaps.append({"record_id": str(record.id), "category": record.category, "title": record.title, "gap": "مالک تعیین نشده است"})
        if record.category == "kpis" and not data.get("target"):
            gaps.append({"record_id": str(record.id), "category": record.category, "title": record.title, "gap": "هدف کمی ثبت نشده است"})
        if record.category == "risks" and not data.get("mitigation"):
            gaps.append({"record_id": str(record.id), "category": record.category, "title": record.title, "gap": "برنامه پاسخ ثبت نشده است"})
        if record.category == "objectives" and not data.get("strategy"):
            gaps.append({"record_id": str(record.id), "category": record.category, "title": record.title, "gap": "به استراتژی متصل نیست"})
    return {"gap_count": len(gaps), "items": gaps}

@app.post("/api/scoring/weighted")
def calculate_weighted_score(payload: WeightedScoreRequest):
    total_weight = sum(item.weight for item in payload.items)
    if not payload.normalize_weights and abs(total_weight - 100) > 0.001:
        raise HTTPException(422, "مجموع وزن‌ها باید دقیقاً ۱۰۰ باشد")
    divisor = total_weight if payload.normalize_weights else 100
    score = sum(item.score * item.weight for item in payload.items) / divisor
    return {"weighted_score": round(score, 2), "total_weight": total_weight, "normalized": payload.normalize_weights}
