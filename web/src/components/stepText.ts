import type { TraceResult, TraceStep } from '../python/protocol.ts'

// The sentence above the player for each step (ADR-0022). Kept apart from
// StepThrough.tsx so that file exports only a component.

/** "Line 3 is about to run, inside double()." and the like. */
export function describeStep(step: TraceStep, trace: TraceResult): string {
  const inner = step.frames.at(-1)
  const where =
    inner && inner.name !== 'program' ? `, inside ${inner.name}()` : ''
  if (step.event === 'call' && inner) {
    const args = inner.vars
      .map(([name, value]) => `${name} = ${value}`)
      .join(', ')
    return `Calling ${inner.name}(${args}).`
  }
  if (step.event === 'return') {
    if (!inner || inner.name === 'program') return 'The program ends.'
    return `${inner.name}() returns ${inner.returns ?? 'nothing'}.`
  }
  if (step.event === 'exception') {
    const summary = trace.error?.trim().split('\n').at(-1)
    return summary
      ? `Error at line ${step.line}${where}: ${summary}`
      : `Error at line ${step.line}${where}.`
  }
  return `Line ${step.line} is about to run${where}.`
}
