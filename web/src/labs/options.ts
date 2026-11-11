// How a lab's container is started (ADR-0018): the `lab:` block of its
// exercise.yaml, which tools/content_model.py calls LabOptions.
import type { Exercise } from '../content/types.ts'

type LabOptions = { init?: 'none' | 'systemd' }

/**
 * Whether the checker starts this lab's container privileged. It does for a
 * lab that boots systemd, `lab: { init: systemd }` (tools/labcheck.py,
 * run_arguments), which is most of them.
 *
 * The page's Exercise type doesn't list `lab`, but the loader copies every
 * field of exercise.yaml onto the exercise (web/src/content/content.ts), so
 * it is there to read. options.test.ts checks that against real labs.
 */
export function runsPrivileged(exercise: Exercise): boolean {
  const options = (exercise as Exercise & { lab?: LabOptions | null }).lab
  return options?.init === 'systemd'
}
