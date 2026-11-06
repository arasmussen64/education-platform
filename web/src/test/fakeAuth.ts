import type { Session, User } from '@supabase/supabase-js'
import { vi } from 'vitest'
import type { AuthClient } from '../auth/authContext.ts'

type Listener = (event: string, session: Session | null) => void

/** A learner as Supabase describes them, with only what the app reads. */
export function fakeUser(overrides: Partial<User> = {}): User {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    email: 'ada@example.com',
    user_metadata: { user_name: 'ada' },
    app_metadata: {},
    aud: 'authenticated',
    created_at: '2026-11-06T00:00:00Z',
    ...overrides,
  } as User
}

/**
 * A stand-in for Supabase's sign-in API. It starts signed in as `user` (or
 * signed out), records calls, and signOut() really signs the fake out.
 */
export function fakeAuth(user: User | null = null) {
  let listener: Listener | null = null
  const sessionFor = (u: User) => ({ user: u }) as Session

  const fake = {
    onAuthStateChange: vi.fn((callback: Listener) => {
      listener = callback
      // Like Supabase: report the current session straight away.
      callback('INITIAL_SESSION', user ? sessionFor(user) : null)
      return { data: { subscription: { unsubscribe: vi.fn() } } }
    }),
    signInWithOAuth: vi.fn(async () => ({ data: {}, error: null })),
    signInWithOtp: vi.fn(async () => ({ data: {}, error: null })),
    signOut: vi.fn(async () => {
      listener?.('SIGNED_OUT', null)
      return { error: null }
    }),
  }
  return fake as typeof fake & AuthClient
}
