import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { renderApp } from '../test/renderApp.tsx'

afterEach(() => {
  vi.unstubAllEnvs()
})

describe('signing in and out', () => {
  // These check the header, so they use the map, a page that needs no
  // history (Today loads the signed-in learner's history from the server).
  it('offers to sign in when nobody is signed in', () => {
    renderApp('/map')
    expect(screen.getByRole('link', { name: 'Sign in' })).toBeInTheDocument()
  })

  it("shows who's signed in, and signs them out", async () => {
    const auth = fakeAuth(fakeUser({ user_metadata: { name: 'Ada Lovelace' } }))
    renderApp('/map', auth)
    expect(screen.getByText('Ada Lovelace')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Sign out' }))
    expect(auth.signOut).toHaveBeenCalled()
    expect(
      await screen.findByRole('link', { name: 'Sign in' }),
    ).toBeInTheDocument()
  })

  it('signs in with GitHub on the live site', async () => {
    vi.stubEnv('DEV', false)
    const { auth } = renderApp('/sign-in')
    await userEvent.click(
      screen.getByRole('button', { name: 'Sign in with GitHub' }),
    )
    expect(auth.signInWithOAuth).toHaveBeenCalledWith({
      provider: 'github',
      options: { redirectTo: `${window.location.origin}/` },
    })
  })

  it('says so when GitHub sign-in fails to start', async () => {
    vi.stubEnv('DEV', false)
    const auth = fakeAuth()
    auth.signInWithOAuth.mockResolvedValueOnce({
      data: {},
      error: new Error('GitHub sign-in is not enabled'),
    } as never)
    renderApp('/sign-in', auth)
    await userEvent.click(
      screen.getByRole('button', { name: 'Sign in with GitHub' }),
    )
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'GitHub sign-in is not enabled',
    )
  })

  it('uses email links during local development', async () => {
    vi.stubEnv('DEV', true)
    const user = userEvent.setup()
    const { auth } = renderApp('/sign-in')
    expect(
      screen.queryByRole('button', { name: 'Sign in with GitHub' }),
    ).not.toBeInTheDocument()

    await user.type(screen.getByLabelText('Email'), 'ada@example.com')
    await user.click(
      screen.getByRole('button', { name: 'Email me a sign-in link' }),
    )
    expect(auth.signInWithOtp).toHaveBeenCalledWith({
      email: 'ada@example.com',
      options: { emailRedirectTo: `${window.location.origin}/` },
    })
    expect(await screen.findByText(/local test inbox/)).toBeInTheDocument()
  })

  it('tells a signed-in learner they are signed in', () => {
    renderApp('/sign-in', fakeAuth(fakeUser()))
    expect(
      screen.getByRole('heading', { name: 'Signed in' }),
    ).toBeInTheDocument()
    expect(screen.getByText(/Signed in as ada/)).toBeInTheDocument()
  })
})
