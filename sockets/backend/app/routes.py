from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import User, Room, RoomMember, Message
from .auth import hash_password, verify_password, create_token, decode_token


router = APIRouter()

def get_bearer_user_id(authorization: str | None) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.replace("Bearer ", "").strip()
    return decode_token(token)

@router.post("/auth/register")
async def register(payload: dict, db: AsyncSession= Depends(get_db)):
    email = (payload.get("email") or "").strip().lower()
    full_name = (payload.get("full_name") or "").strip()
    password = payload.get("password") or ""

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password is required")
    
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(email= email, full_name= full_name or "User", password_has = hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token= create_token(user.id)
    return {
         "user": {"token": token, "id": user.id, "email": user.email, "full_name": user.full_name}
    }

@router.post("/auth/login")
async def login(payload: dict, db: AsyncSession = Depends(get_db)):
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    q = await db.execute(select(User).where(User.email == email))
    user = q.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user.id)
    return {"token": token, "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}

@router.post("/room/create")
async def create_room(payload: dict, authorization: str | None=None, db: AsyncSession = Depends(get_db)):
    user_id = get_bearer_user_id(authorization)
    title = (payload.get("title") or "").strip()

    if not title:
        raise HTTPException(status_code=400, detail="title required")
    
    room = Room(title = title)
    db.add(room)
    await db.commit()
    await db.refresh(room)

    db.add(RoomMember(room_id= room.id, user_id=user_id))
    await db.commit()

    return{
        "room": {"id": room.id, "title": room.title}
    }

@router.get("/rooms")
async def list_rooms(authorization: str | None = None, db: AsyncSession = Depends(get_db)):
    user_id = get_bearer_user_id(authorization)

    q = await db.execute(
        select(Room.id, Room.title)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id==user_id)
        .order_by(Room.id.desc())
    )

    rooms = [{"id": r[0], "title": r[1]} for r in q.all()]
    return {
        "rooms": rooms
    }

@router.get("/room/{room_id}/messages")
async def get_messages(room_id: int, authorization: str | None= None, db: AsyncSession = Depends(get_db)):
    user_id = get_bearer_user_id(authorization)

    m = await db.execute(
        select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
    )

    if not m.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this room")
    
    q = await db.execute(
        select(Message.id, Message.user_id, Message.content, Message.created_at)
        .where(Message.room_id == room_id)
        .order_by(Message.id.asc())
        .limit(200)
    )

    messages = [
        {"id": row[0], "user_id": row[1], "content": row[2], "created_at": str(row[3])}
        for row in q.all()
    ]
    return {
        "messages": messages
    }