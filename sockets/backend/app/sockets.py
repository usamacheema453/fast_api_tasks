import socketio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from .auth import decode_token
from .models import RoomMember, Message

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

connected = {}


async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@sio.event
async def connect(sid, environ, auth):
    try:
        token = (auth or {}).get("token", "")
        user_id = decode_token(token)
        connected[sid] = user_id
        print("connected", sid, "user", user_id)
        return True
    except Exception:
        return False
    
@sio.event
async def disconnect(sid):
    connected.pop(sid, None)
    print("Disconnected ", sid)


@sio.event
async def join_room(sid, data):
    room_id = data["room_id"]
    await sio.enter_room(sid, str(room_id))



@sio.event
async def typing(sid, data):
    user_id = connected.get(sid)
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
    user_id = connected[sid]
    room_id = data["room_id"]
    content = data["content"]

    async with AsyncSession() as db:
        msg = Message(room_id= room_id, user_id=user_id, content = content)
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

        await sid.emit("new_message", payload, room= str(room_id))