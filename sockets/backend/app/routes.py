from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .database import get_db
from .models import User, Room, RoomMember, Message
from .auth import hash_password, verify_password, create_token, decode_token


router = APIRouter()

def get_bearer_user_id(authorization: str | None) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.replace("Bearer ", "").strip()
    return decode_token(token)

@router.get("/users")
async def users(authorization: str | None = Header(None), db: AsyncSession = Depends(get_db)):
    user_id = get_bearer_user_id(authorization)
    q = await db.execute(select(User.id, User.email, User.full_name).where(User.id != user_id))
    return {
        "users":[ {"id": r[0], "email": r[1], "full_name": r[2]} for r in q.all()]
    }

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
    
    user = User(email= email, full_name= full_name or "User", password_hash = hash_password(password))
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


@router.post("/chat/start")
async def start_chat(payload: dict, authorization: str | None = Header(None), db : AsyncSession = Depends(get_db)):
    user_id = get_bearer_user_id(authorization)
    others = payload["user_id"]

    q = await db.execute(
        select(Room.id)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id.in_([user_id, others]))
        .group_by(Room.id)
        .having(func.count(RoomMember.user_id) == 2)
    )

    room = q.scalar_one_or_none()

    if room:
        return {"room_id": room}
    
    room = Room()
    db.add(room)
    await db.commit()
    await db.refresh(room)

    db.add_all([
        RoomMember(room_id = room.id, user_id= user_id),
        RoomMember(room_id=room.id, user_id=others)
    ])
    await db.commit()

    return {"room_id": room.id}


@router.get("/messages/{room_id}")
async def messages(room_id: int, authorization: str | None= Header(None), db: AsyncSession= Depends(get_db)):
    user_id = get_bearer_user_id(authorization)

    q = await db.execute(
        select(Message.id, Message.user_id, Message.content, Message.created_at)
        .where(Message.room_id == room_id)
        .order_by(Message.id)
    )

    return {
        "messages": [
            {"id": r[0], "user_id": r[1], "content": r[2], "created_at": str(r[3])}
            for r in q.all()
        ]
    }