// The words of the "How it's marked" note (HowItsMarked.tsx), kept apart
// from the component so they can be tested on their own.

/** "one", "two" … as a sentence writes a small number; digits past nine. */
function inWords(count: number): string {
  return (
    [
      'no',
      'one',
      'two',
      'three',
      'four',
      'five',
      'six',
      'seven',
      'eight',
      'nine',
    ][count] ?? String(count)
  )
}

/** "Your explanation is checked against six points …" */
export function pointsSentence(
  total: number,
  required: number,
  extra: number,
): string {
  const start = `Your explanation is checked against ${
    total === 1 ? 'one point' : `${inWords(total)} points`
  }, drawn from the question above`
  if (total === 1) return `${start}, and a pass needs it.`
  if (extra === 0) return `${start}, and a pass needs every one.`
  return `${start}: ${inWords(required)} needed to pass, and ${inWords(extra)} extra that ${
    extra === 1 ? "isn't" : "aren't"
  } needed.`
}
