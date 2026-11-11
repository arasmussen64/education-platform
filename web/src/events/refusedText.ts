// The words a learner reads about refused events: ones the server wouldn't
// take, which stay on this device and are tried again (see sync.ts). They're
// here so the header and the account page always say the same thing.
//
// A refused event can be an answer, a Run, a lesson opened and so on, so the
// text says "work" and not "answers".

/** "1 piece of your work couldn't be saved yet", or "3 pieces of …". */
export function couldNotSave(count: number): string {
  const pieces =
    count === 1
      ? '1 piece of your work'
      : `${count.toLocaleString('en-US')} pieces of your work`
  return `${pieces} couldn't be saved yet`
}

/** What happens to them, said about one event or about several. */
export function keptAndRetried(count: number): string {
  return count === 1
    ? "It's kept on this device and will be tried again."
    : "They're kept on this device and will be tried again."
}
