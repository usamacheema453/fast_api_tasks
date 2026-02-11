'use client';

import { useState } from 'react';
import { Message, User } from '@/app/page';

export default function ChatSection({
  messages = [],
  onSendMessage,
  currentUserId,
  chatUser
}: {
  messages?: Message[];
  onSendMessage: (t: string) => void;
  currentUserId: number;
  chatUser: User;
}) {
  const [text, setText] = useState("");

  const send = () => {
    if (!text.trim()) return;
    onSendMessage(text);
    setText("");
  };

  return (
    <div className="bg-white p-4 rounded shadow h-[500px] flex flex-col">
      <h2 className="font-bold mb-4 text-gray-900">
        Chat with {chatUser?.email}
      </h2>

      <div className="flex-1 overflow-auto space-y-2">
        {(messages || []).map(m => (
          <div key={m.id} className={m.user_id === currentUserId ? "text-right" : ""}>
            <div className="inline-block bg-blue-200 p-2 rounded text-gray-700">
              {m.content}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2 mt-2">
        <input
          value={text}
          onChange={e => setText(e.target.value)}
          className="border p-2 flex-1 text-black"
        />
        <button onClick={send} className="bg-blue-600 text-white px-4">
          Send
        </button>
      </div>
    </div>
  );
}
