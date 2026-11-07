import { afterEach, describe, expect, it, vi } from 'vitest'
import { downloadJson } from './download.ts'

// jsdom can't make file addresses or download anything, so stand-ins record
// what the browser would have been asked to do.
const original = {
  create: URL.createObjectURL,
  revoke: URL.revokeObjectURL,
}

afterEach(() => {
  URL.createObjectURL = original.create
  URL.revokeObjectURL = original.revoke
  vi.restoreAllMocks()
  vi.useRealTimers()
})

describe('downloadJson', () => {
  it('saves the value as a readable JSON file, then frees the memory', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout'] })
    const files: Blob[] = []
    URL.createObjectURL = vi.fn((file: Blob | MediaSource) => {
      files.push(file as Blob)
      return 'blob:file-1'
    })
    URL.revokeObjectURL = vi.fn()
    const clicked: { download: string; href: string; onPage: boolean }[] = []
    vi.spyOn(HTMLElement.prototype, 'click').mockImplementation(function (
      this: HTMLElement,
    ) {
      const link = this as HTMLAnchorElement
      clicked.push({
        download: link.download,
        href: link.href,
        onPage: document.body.contains(link),
      })
    })

    downloadJson('data.json', { events: [1, 2] })

    // A link to the file was clicked while on the page, then taken away.
    expect(clicked).toEqual([
      { download: 'data.json', href: 'blob:file-1', onPage: true },
    ])
    expect(document.querySelector('a')).toBeNull()
    // The memory is freed a minute later, once the download has started.
    expect(URL.revokeObjectURL).not.toHaveBeenCalled()
    vi.advanceTimersByTime(60_000)
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:file-1')

    vi.useRealTimers()
    expect(files[0]?.type).toBe('application/json')
    expect(await files[0]?.text()).toBe(
      '{\n  "events": [\n    1,\n    2\n  ]\n}',
    )
  })
})
