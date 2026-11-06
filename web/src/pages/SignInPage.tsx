import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'
import { displayName } from '../auth/authContext.ts'
import { useAuth } from '../auth/useAuth.ts'
import { BUTTON, TEXT_INPUT } from '../components/styles.ts'
import { signInMethod } from '../supabase/config.ts'

function describe(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

// Signing in is what lets the platform save progress (v1 spec, F1).
export function SignInPage() {
  const auth = useAuth()

  if (auth.status === 'loading') {
    return <p className="text-slate-500 dark:text-slate-400">Loading…</p>
  }

  if (auth.status === 'signed-in') {
    return (
      <section className="space-y-2">
        <h1 className="text-2xl font-bold">Signed in</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Signed in as {displayName(auth.user)}.{' '}
          <Link to="/" className="underline">
            Go to Today
          </Link>
        </p>
      </section>
    )
  }

  return (
    <section className="max-w-md space-y-4">
      <h1 className="text-2xl font-bold">Sign in</h1>
      <p className="text-slate-600 dark:text-slate-400">
        Sign in to save your progress.
      </p>
      {signInMethod() === 'github' ? <GitHubSignIn /> : <EmailLinkSignIn />}
    </section>
  )
}

/** The live site: GitHub checks who you are, then sends you back here. */
function GitHubSignIn() {
  const { signInWithGitHub } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleClick() {
    setBusy(true)
    setError('')
    try {
      // On success the browser leaves for GitHub, so there's nothing more to do.
      await signInWithGitHub()
    } catch (err) {
      setError(describe(err))
      setBusy(false)
    }
  }

  return (
    <div className="space-y-2">
      <button
        type="button"
        onClick={handleClick}
        disabled={busy}
        className={BUTTON}
      >
        Sign in with GitHub
      </button>
      {error && (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300">
          Sign-in didn&apos;t start: {error}
        </p>
      )}
    </div>
  )
}

/** Local development only: the email arrives in the local test inbox. */
function EmailLinkSignIn() {
  const { sendSignInLink } = useAuth()
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    try {
      await sendSignInLink(email)
      setSent(true)
    } catch (err) {
      setError(describe(err))
    }
  }

  if (sent) {
    return (
      <output className="block text-slate-600 dark:text-slate-400">
        Sign-in link sent. Open the local test inbox at{' '}
        <a href="http://127.0.0.1:54324" className="underline">
          127.0.0.1:54324
        </a>{' '}
        and click the link in the email.
      </output>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Local development: the local Supabase has no GitHub sign-in, so you sign
        in with an email link instead. Any address works. The email lands in the
        local test inbox, not a real mailbox.
      </p>
      <label className="block text-sm">
        <span className="font-medium">Email</span>
        <input
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className={TEXT_INPUT}
        />
      </label>
      <button type="submit" className={BUTTON}>
        Email me a sign-in link
      </button>
      {error && (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300">
          The link wasn&apos;t sent: {error}
        </p>
      )}
    </form>
  )
}
