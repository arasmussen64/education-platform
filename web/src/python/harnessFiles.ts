// The shared Python harness (see harness/README.md), bundled into the app as
// text. The same files run in CI, so a learner's code gets the same verdict
// in the browser as on GitHub.
import checks from '../../../harness/checks.py?raw'
import errors from '../../../harness/errors.py?raw'
import program from '../../../harness/program.py?raw'
import testrunner from '../../../harness/testrunner.py?raw'
import tracer from '../../../harness/tracer.py?raw'

export const HARNESS_FILES: readonly { name: string; source: string }[] = [
  { name: 'checks.py', source: checks },
  { name: 'errors.py', source: errors },
  { name: 'program.py', source: program },
  { name: 'testrunner.py', source: testrunner },
  { name: 'tracer.py', source: tracer },
]
