// Where the app's database and sign-in live (Supabase).
//
// These values are public by design: every browser needs them, and the
// database's row-level security decides what each signed-in learner may read
// and write (see supabase/migrations). Secret keys never appear in app code.

type SupabaseSettings = { url: string; publishableKey: string }

/** The dev server (npm run dev) uses the local Supabase in Docker (ADR-0010). */
const LOCAL: SupabaseSettings = {
  url: 'http://127.0.0.1:54321',
  // The local Supabase's default key (see `npm run db:status`).
  publishableKey: 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH',
}

/** The built app (the live site) uses the real project. */
const PRODUCTION: SupabaseSettings = {
  url: 'https://fretenazxzmfakjxvtwd.supabase.co',
  publishableKey: 'sb_publishable_lZ5Jtsn7e-Sc55vZbKC4Cg_3RkxLq74',
}

export function supabaseSettings(): SupabaseSettings {
  return import.meta.env.DEV ? LOCAL : PRODUCTION
}

/**
 * The live site signs in with GitHub. The local Supabase has no GitHub app,
 * so local development signs in with email links instead; they land in the
 * local test inbox (Mailpit, http://127.0.0.1:54324).
 */
export function signInMethod(): 'github' | 'email-link' {
  return import.meta.env.DEV ? 'email-link' : 'github'
}
