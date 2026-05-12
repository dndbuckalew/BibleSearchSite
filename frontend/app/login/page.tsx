'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleLogin = () => {
    const expectedUser = process.env.NEXT_PUBLIC_BTA_TEST_USER;
    const expectedPass = process.env.NEXT_PUBLIC_BTA_TEST_PASS;

    if (username === expectedUser && password === expectedPass) {
      sessionStorage.setItem('bta_authenticated', 'true');
      router.push('/');
    } else {
      setError('Invalid credentials');
    }
  };

  return (
    <section className="max-w-md mx-auto mt-16 space-y-6">
      <h2 className="text-2xl font-semibold">Version 2 Access</h2>

      <div className="text-sm text-neutral-600">
        This system is in limited Version 2.1.2. Please enter your invitation credentials.
      </div>

      <div className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full rounded-md border px-3 py-2 text-sm"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border px-3 py-2 text-sm"
        />

        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}

        <button
          onClick={handleLogin}
          className="w-full rounded-md border border-neutral-400 bg-neutral-50 px-4 py-3 text-sm font-medium hover:bg-neutral-100"
        >
          Enter
        </button>
      </div>
    </section>
  );
}
