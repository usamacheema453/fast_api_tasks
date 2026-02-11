'use client';

import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import AuthSection from '@/components/AuthSection';
import UserList from '@/components/UserList';
import ChatSection from '@/components/ChatSection';

const API_URL = 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
}

export interface Message {
  id: number;
  user_id: number;
  content: string;
  created_at: string;
}

export default function Home() {
  const [token, setToken] = useState<string>('');
  const [user, setUser] = useState<User | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const [users, setUsers] = useState<User[]>([]);
  const [currentChatUser, setCurrentChatUser] = useState<User | null>(null);
  const [roomId, setRoomId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  // restore login
  useEffect(() => {
    const t = localStorage.getItem("token");
    const u = localStorage.getItem("user");

    if (t && u) {
      setToken(t);
      setUser(JSON.parse(u));
    }
  }, []);

  // socket connect
  useEffect(() => {
    if (token && !socket) {
      const s = io(API_URL, { auth: { token } });

      s.on("connect", () => {
        setIsConnected(true);
      });

      s.on("disconnect", () => setIsConnected(false));

      s.on("new_message", (msg: Message) => {
        setMessages(prev => [...prev, msg]);
      });

      setSocket(s);

      return () => s.close();
    }
  }, [token]);

  // fetch users
  useEffect(() => {
    if (token) fetchUsers();
  }, [token]);

  const fetchUsers = async () => {
    const res = await fetch(`${API_URL}/api/users`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    setUsers(data.users);
  };

  const handleLogin = (t: string, u: User) => {
    localStorage.setItem("token", t);
    localStorage.setItem("user", JSON.stringify(u));
    setToken(t);
    setUser(u);
  };

  const startChat = async (other: User) => {
    setCurrentChatUser(other);

    const res = await fetch(`${API_URL}/api/chat/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ user_id: other.id })
    });

    const data = await res.json();
    setRoomId(data.room_id);

    // fetch messages
    const m = await fetch(`${API_URL}/api/messages/${data.room_id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const md = await m.json();
    setMessages(md.messages || []);

    socket?.emit("join_room", { room_id: data.room_id });
  };

  const sendMessage = (text: string) => {
    if (!roomId) return;
    socket?.emit("send_message", { room_id: roomId, content: text });
  };

  return (
    <div className="p-10">
      {!token ? (
        <AuthSection onLogin={handleLogin} apiUrl={API_URL} />
      ) : (
        <div className="grid grid-cols-3 gap-4">
          <UserList users={users} onSelect={startChat} />

          <div className="col-span-2">
            {currentChatUser && (
              <ChatSection
                messages={messages}
                onSendMessage={sendMessage}
                currentUserId={user?.id || 0}
                chatUser={currentChatUser}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
