'use client';

import { User } from '@/app/page';

export default function UserList({
  users,
  onSelect
}: {
  users: User[];
  onSelect: (u: User) => void;
}) {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-bold mb-4 text-black">Users</h2>

      {users.map(u => (
        <div
          key={u.id}
          onClick={() => onSelect(u)}
          className="p-2 cursor-pointer hover:bg-gray-100 text-gray-700"
        >
          {u.email}
        </div>
      ))}
    </div>
  );
}
