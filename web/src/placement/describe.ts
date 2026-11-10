// One-line summaries of a finished placement (ADR-0021), for the placement
// page's cards and the Today page.
import { getTopic } from '../content/content.ts'
import type { Diagnostic } from '../content/types.ts'
import { dayOf } from '../days.ts'
import type { PlacementRecord } from './history.ts'

/** "Placement on 2026-11-09: start at Loops, with 6 topics to prove first." */
export function describeTrackRecord(
  record: PlacementRecord,
  learned: (topicId: string) => boolean,
): string {
  const toProve = record.known.filter((id) => !learned(id))
  const next = record.next ? getTopic(record.next)?.title : undefined
  const start = next
    ? `start at ${next}`
    : 'everything written so far looked familiar'
  const prove =
    toProve.length === 0
      ? ''
      : toProve.length === 1
        ? ', with 1 topic to prove first'
        : `, with ${toProve.length} topics to prove first`
  return `Placement on ${dayOf(record.at)}: ${start}${prove}.`
}

/** "Placement on 2026-11-09: solid through Algebra; refresh from Functions." */
export function describeDiagnosticRecord(
  record: PlacementRecord,
  diagnostic: Diagnostic,
): string {
  const day = dayOf(record.at)
  const titleOf = (id: string | null | undefined) =>
    diagnostic.levels.find((level) => level.id === id)?.title
  const next = titleOf(record.next)
  if (!next) return `Placement on ${day}: every level looked solid.`
  const through = titleOf(record.known.at(-1))
  return `Placement on ${day}: ${through ? `solid through ${through}; ` : ''}refresh from ${next}.`
}
