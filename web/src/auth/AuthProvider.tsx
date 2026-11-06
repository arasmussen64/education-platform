import { type ReactNode, useEffect, useMemo, useState } from 'react'
import { getSupabase } from '../supabase/client.ts'
import {
  type AuthClient,
  AuthContext,
  type AuthState,
  type AuthValue,
} from './authContext.ts'

type Props = {
  children: ReactNode
  /** Tests pass a fake; the app uses the real Supabase client. */
  auth?: AuthClient
}

/** Keeps track of who's signed in and shares it with the whole app. */
export function AuthProvider({ children, auth }: Props) {
  const client = auth ?? getSupabase().auth
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  useEffect(() => {
    // Supabase reports the current session straight away, then every change
    // (signing in, signing out, a session expiring).
    const { data } = client.onAuthStateChange((_event, session) => {
      setState(
        session
          ? { status: 'signed-in', user: session.user }
          : { status: 'signed-out' },
      )
    })
    return () => data.subscription.unsubscribe()
  }, [client])

  const value = useMemo<AuthValue>(
    () => ({
      ...state,
      async signInWithGitHub() {
        const { error } = await client.signInWithOAuth({
          provider: 'github',
          options: { redirectTo: `${window.location.origin}/` },
        })
        if (error) throw error
      },
      async sendSignInLink(email: string) {
        const { error } = await client.signInWithOtp({
          email,
          options: { emailRedirectTo: `${window.location.origin}/` },
        })
        if (error) throw error
      },
      async signOut() {
        const { error } = await client.signOut()
        if (error) throw error
      },
    }),
    [client, state],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
