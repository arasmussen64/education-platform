import { CodeRunner } from '../components/CodeRunner.tsx'

const GREETING = `name = input("What's your name? ")
print(f"Hello, {name}!")
`

const SWAP_START = `x = 3
y = 5

# Swap the values of x and y here.

print(x)
print(y)
`

// The same kind of test file that exercises use (docs/specs/data-model.md).
const SWAP_TESTS = `from checks import run


def test_swaps():
    """Prints the swapped values: 5, then 3."""
    assert run() == "5\\n3\\n"
`

// A temporary page for trying the Python runner until topic pages exist.
export function PlaygroundPage() {
  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-2xl font-bold">Playground</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Write and run Python right in your browser. Nothing here is saved yet.
        </p>
      </section>

      <section aria-labelledby="run-anything" className="space-y-3">
        <h2 id="run-anything" className="text-lg font-semibold">
          Run anything
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Type a name in the input box, then press Run.
        </p>
        <CodeRunner initialCode={GREETING} />
      </section>

      <section aria-labelledby="try-a-check" className="space-y-3">
        <h2 id="try-a-check" className="text-lg font-semibold">
          Try a check
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Swap x and y so the program prints 5, then 3. Press Check to see
          whether it works.
        </p>
        <CodeRunner initialCode={SWAP_START} tests={SWAP_TESTS} />
      </section>
    </div>
  )
}
