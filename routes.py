from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import SessionLocal, Bookmark
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
import json
import requests
from bs4 import BeautifulSoup
from ai_service import generate_ai_tags

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Pydantic Schemas ----------
class BookmarkCreate(BaseModel):
    url: HttpUrl
    tags: Optional[List[str]] = Field(default_factory=list)

class BookmarkRead(BaseModel):
    id: int
    url: str
    title: Optional[str]
    tags: List[str]
    created_at: str

    class Config:
        orm_mode = True

class PreviewRequest(BaseModel):
    url: HttpUrl

class PreviewResponse(BaseModel):
    title: Optional[str]
    url: str

class AiTagsRequest(BaseModel):
    model: Optional[str] = None  # future extension
    max_tags: int = Field(default=5, ge=1, le=10)

class AiTagsResponse(BaseModel):
    suggested_tags: List[str]

# ---------- Helper ----------
def fetch_title(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else None
    except Exception:
        return None

# ---------- Endpoints ----------
@router.post("/bookmarks", response_model=BookmarkRead)
def create_bookmark(payload: BookmarkCreate, db: Session = Depends(get_db)):
    title = fetch_title(payload.url)
    db_bookmark = Bookmark(url=payload.url, title=title, tags=payload.tags)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return BookmarkRead.from_orm(db_bookmark)

@router.get("/bookmarks", response_model=List[BookmarkRead])
def list_bookmarks(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Bookmark)
    if search:
        like_term = f"%{search}%"
        query = query.filter(
            Bookmark.title.ilike(like_term) | Bookmark.url.ilike(like_term) | Bookmark.tags.cast(String).ilike(like_term)
        )
    results = query.order_by(Bookmark.created_at.desc()).all()
    return [BookmarkRead.from_orm(b) for b in results]

@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkRead)
def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    bookmark = db.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return BookmarkRead.from_orm(bookmark)

@router.post("/bookmarks/preview", response_model=PreviewResponse)
def preview_url(request: PreviewRequest):
    title = fetch_title(request.url)
    return PreviewResponse(title=title, url=request.url)

@router.post("/bookmarks/{bookmark_id}/ai-tags", response_model=AiTagsResponse)
async def ai_tags(bookmark_id: int, req: AiTagsRequest, db: Session = Depends(get_db)):
    bookmark = db.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    tags = await generate_ai_tags(bookmark.title or "", bookmark.url, max_tags=req.max_tags)
    # Optionally persist suggested tags (not overriding user tags)
    return AiTagsResponse(suggested_tags=tags)

@router.get("/export")
def export_bookmarks(db: Session = Depends(get_db)):
    bookmarks = db.query(Bookmark).all()
    data = [
        {
            "id": b.id,
            "url": b.url,
            "title": b.title,
            "tags": b.tags,
            "created_at": b.created_at.isoformat(),
        }
        for b in bookmarks
    ]
    return JSONResponse(content=data)

@router.post("/import")
def import_bookmarks(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = file.file.read()
        items = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    imported = 0
    for item in items:
        url = item.get("url")
        if not url:
            continue
        existing = db.query(Bookmark).filter(Bookmark.url == url).first()
        if existing:
            continue
        bm = Bookmark(
            url=url,
            title=item.get("title"),
            tags=item.get("tags", []),
        )
        db.add(bm)
        imported += 1
    db.commit()
    return {"imported": imported}
