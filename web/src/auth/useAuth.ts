import { useContext } from 'react'
import { AuthContext, type AuthValue } from './authContext.ts'

/** Who's signed in, and the sign-in and sign-out actions. */
export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>')
  return value
}
