import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { supabaseSettings } from './config.ts'
import type { Database } from './database.types.ts'

let client: SupabaseClient<Database> | null = null

/**
 * The app's one Supabase client, created the first time it's needed.
 * Sign-in sessions are kept in the browser's local storage and refreshed
 * automatically.
 */
export function getSupabase(): SupabaseClient<Database> {
  if (!client) {
    const { url, publishableKey } = supabaseSettings()
    client = createClient<Database>(url, publishableKey, {
      auth: {
        // PKCE is the safest sign-in flow for apps that run entirely in the
        // browser. supabase-js then also removes the one-time ?code=... from
        // the address bar after signing in.
        flowType: 'pkce',
      },
    })
  }
  return client
}
