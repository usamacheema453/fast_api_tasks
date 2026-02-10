'use client';

import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import AuthSection from '@/components/AuthSection';
import RoomSection from '@/components/RoomSection';
import ChatSection from '@/components/ChatSection';

const API_URL = 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  full_name: string;
}

export interface Room {
  id: number;
  title: string;
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
  const [currentRoom, setCurrentRoom] = useState<Room | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [typingUsers, setTypingUsers] = useState<number[]>([]);

  // Socket.IO connection
  useEffect(() => {
    if (token && !socket) {
      const newSocket = io(API_URL, {
        auth: { token }
      });

      newSocket.on('connect', () => {
        console.log('Socket connected:', newSocket.id);
        setIsConnected(true);
      });

      newSocket.on('disconnect', () => {
        console.log('Socket disconnected');
        setIsConnected(false);
      });

      newSocket.on('error', (error: any) => {
        console.error('Socket error:', error);
        alert(error.message || 'Socket error occurred');
      });

      newSocket.on('joined', (data: any) => {
        console.log('Joined room:', data);
      });

      newSocket.on('typing', (data: { user_id: number; is_typing: boolean }) => {
        setTypingUsers(prev => {
          if (data.is_typing) {
            return prev.includes(data.user_id) ? prev : [...prev, data.user_id];
          } else {
            return prev.filter(id => id !== data.user_id);
          }
        });
      });

      newSocket.on('new_message', (msg: Message) => {
        console.log('New message:', msg);
        setMessages(prev => [...prev, msg]);
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
      };
    }
  }, [token]);

  // Fetch rooms when user logs in
  useEffect(() => {
    if (token) {
      fetchRooms();
    }
  }, [token]);

  const fetchRooms = async () => {
    try {
      const res = await fetch(`${API_URL}/api/rooms`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await res.json();
      setRooms(data.rooms || []);
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
  };

  const handleLogin = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
  };

  const handleRoomCreated = (room: Room) => {
    setRooms(prev => [room, ...prev]);
  };

  const handleRoomSelect = async (room: Room) => {
    setCurrentRoom(room);
    
    // Fetch messages
    try {
      const res = await fetch(`${API_URL}/api/room/${room.id}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }

    // Join room via socket
    if (socket) {
      socket.emit('join_room', { room_id: room.id });
    }
  };

  const handleSendMessage = (content: string) => {
    if (socket && currentRoom) {
      socket.emit('send_message', {
        room_id: currentRoom.id,
        content
      });
    }
  };

  const handleTyping = (isTyping: boolean) => {
    if (socket && currentRoom) {
      socket.emit('typing', {
        room_id: currentRoom.id,
        is_typing: isTyping
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center text-indigo-900 mb-8">
          💬 FastAPI Chat Application
        </h1>

        {!token ? (
          <AuthSection onLogin={handleLogin} apiUrl={API_URL} />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Sidebar - Rooms */}
            <div className="lg:col-span-1">
              <RoomSection
                token={token}
                rooms={rooms}
                currentRoom={currentRoom}
                onRoomCreated={handleRoomCreated}
                onRoomSelect={handleRoomSelect}
                apiUrl={API_URL}
                isConnected={isConnected}
                user={user}
              />
            </div>

            {/* Right - Chat Area */}
            <div className="lg:col-span-2">
              {currentRoom ? (
                <ChatSection
                  room={currentRoom}
                  messages={messages}
                  currentUserId={user?.id || 0}
                  onSendMessage={handleSendMessage}
                  onTyping={handleTyping}
                  typingUsers={typingUsers}
                />
              ) : (
                <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                  <div className="text-gray-400 text-6xl mb-4">💬</div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    No Room Selected
                  </h3>
                  <p className="text-gray-500">
                    Select a room from the sidebar or create a new one
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}