'use client';

import { useState } from 'react';
import { Room, User } from '@/app/page';

interface RoomSectionProps {
  token: string;
  rooms: Room[];
  currentRoom: Room | null;
  onRoomCreated: (room: Room) => void;
  onRoomSelect: (room: Room) => void;
  apiUrl: string;
  isConnected: boolean;
  user: User | null;
}

export default function RoomSection({
  token,
  rooms,
  currentRoom,
  onRoomCreated,
  onRoomSelect,
  apiUrl,
  isConnected,
  user
}: RoomSectionProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newRoomTitle, setNewRoomTitle] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(`${apiUrl}/api/room/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title: newRoomTitle })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to create room');
      }

      onRoomCreated(data.room);
      setNewRoomTitle('');
      setShowCreateModal(false);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* User Info */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Logged in as</p>
            <p className="font-semibold text-gray-800">{user?.full_name}</p>
            <p className="text-xs text-gray-400">{user?.email}</p>
          </div>
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
      </div>

      {/* Create Room Button */}
      <button
        onClick={() => setShowCreateModal(true)}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 mb-4"
      >
        + Create New Room
      </button>

      {/* Rooms List */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">
          YOUR ROOMS ({rooms.length})
        </h3>
        
        {rooms.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">
            No rooms yet. Create one!
          </p>
        ) : (
          rooms.map(room => (
            <button
              key={room.id}
              onClick={() => onRoomSelect(room)}
              className={`w-full text-left px-4 py-3 rounded-lg transition duration-200 ${
                currentRoom?.id === room.id
                  ? 'bg-indigo-100 border-2 border-indigo-500'
                  : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
              }`}
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">💬</span>
                <div>
                  <p className="font-semibold text-gray-800">{room.title}</p>
                  <p className="text-xs text-gray-500">Room #{room.id}</p>
                </div>
              </div>
            </button>
          ))
        )}
      </div>

      {/* Create Room Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              Create New Room
            </h3>
            <form onSubmit={handleCreateRoom}>
              <input
                type="text"
                value={newRoomTitle}
                onChange={(e) => setNewRoomTitle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4"
                placeholder="Enter room title"
                required
                autoFocus
              />
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-lg transition duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}