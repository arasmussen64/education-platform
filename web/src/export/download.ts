/**
 * Saves `value` as a JSON file, through the browser's normal download. The
 * file is made right here in the browser: nothing is sent anywhere.
 */
export function downloadJson(fileName: string, value: unknown): void {
  // Two-space indents, so the file is readable in any text editor.
  downloadText(fileName, JSON.stringify(value, null, 2), 'application/json')
}

/**
 * Saves `text` as a file of the given type (a calendar file, say), through
 * the browser's normal download. Made in the browser; nothing is sent.
 */
export function downloadText(fileName: string, text: string, type: string) {
  const file = new Blob([text], { type })
  // A temporary address for the file, pointing into the browser's memory.
  const address = URL.createObjectURL(file)
  const link = document.createElement('a')
  link.href = address
  link.download = fileName
  // Some browsers only follow a link that's on the page.
  document.body.append(link)
  link.click()
  link.remove()
  // Free the memory once the download has surely started.
  setTimeout(() => URL.revokeObjectURL(address), 60_000)
}
