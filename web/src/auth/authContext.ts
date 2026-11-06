import type { SupabaseClient, User } from '@supabase/supabase-js'
import { createContext } from 'react'

/** The parts of Supabase's sign-in API the app uses, so tests can pass a fake. */
export type AuthClient = Pick<
  SupabaseClient['auth'],
  'onAuthStateChange' | 'signInWithOAuth' | 'signInWithOtp' | 'signOut'
>

export type AuthState =
  | { status: 'loading' }
  | { status: 'signed-out' }
  | { status: 'signed-in'; user: User }

export type AuthActions = {
  /** Live site: go to GitHub to sign in; GitHub sends the learner back. */
  signInWithGitHub(): Promise<void>
  /** Local development: email a sign-in link (it lands in Mailpit). */
  sendSignInLink(email: string): Promise<void>
  signOut(): Promise<void>
}

export type AuthValue = AuthState & AuthActions

export const AuthContext = createContext<AuthValue | null>(null)

/** A friendly name for the signed-in learner. */
export function displayName(user: User): string {
  const meta = user.user_metadata as Record<string, unknown>
  for (const key of ['full_name', 'name', 'user_name']) {
    const value = meta[key]
    if (typeof value === 'string' && value.trim()) return value
  }
  return user.email ?? 'Signed in'
}
