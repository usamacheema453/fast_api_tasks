import socketio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from .auth import decode_token
from .models import RoomMember, Message

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

connected_users: dict[str, int] ={}


async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@sio.event
async def connect(sid, environ, auth):
    try:
        token = (auth or {}).get("token", "")
        user_id = decode_token(token)
        connected_users[sid] = user_id
        print("connected", sid, "user", user_id)
        return True
    except Exception:
        return False
    
@sio.event
async def disconnect(sid):
    connected_users.pop(sid, None)
    print("Disconnected ", sid)

@sio.event
async def join_room(sid, data):
    user_id = connected_users.get(sid)
    room_id = int(data.get("room_id"))

    async with AsyncSessionLocal() as db:
        q = await db.execute(select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id))
        if not q.scalar_one_or_none():
            await sio.emit("error", {"message": "Not a room member"}, to=sid)
            return
        
    await sio.enter_room(sid, str(room_id))
    await sio.emit("joined", {"room_id": room_id}, to=sid)

@sio.event
async def typing(sid, data):
    user_id = connected_users.get(sid)
    room_id = int(data.get("room_id"))

    is_typing = bool(data.get("is_typing", False))

    await sio.emit(
        "typing",
        {
            "room_id": room_id, "user_id": user_id, "is_typing": is_typing
        },
        room=str(room_id)
    )

@sio.event
async def send_message(sid, data):
    user_id = connected_users.get(sid)
    room_id = int(data.get("room_id"))
    content = (data.get("content") or "").strip()

    if not content:
        await sio.emit("error", {"message": "Empty message"}, to=sid)
        return

    async with AsyncSessionLocal() as db:
        q = await db.execute(select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id))
        if not q.scalar_one_or_none():
            await sio.emit("error", {"message": "Not a room member"}, to=sid)
            return

        msg = Message(room_id=room_id, user_id=user_id, content=content)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)

        payload = {
            "id": msg.id,
            "room_id": room_id,
            "user_id": user_id,
            "content": msg.content,
            "created_at": str(msg.created_at)
        }

    await sio.emit("new_message", payload, room=str(room_id))