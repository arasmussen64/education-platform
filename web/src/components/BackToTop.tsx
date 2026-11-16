import { useEffect, useState } from 'react'

/**
 * A "Back to top" button that floats in the bottom corner of long pages.
 *
 * It appears only once the learner has scrolled more than one screen down,
 * so short pages never show it. A click scrolls to the top (smoothly, unless
 * the learner's system asks for less motion) and moves keyboard focus to
 * `focusTarget`, so the next Tab starts from the top too.
 */
export function BackToTop({
  focusTarget,
}: {
  focusTarget: () => HTMLElement | null
}) {
  const [shown, setShown] = useState(false)

  useEffect(() => {
    // Checked on every scroll, and on resize, since a screen's height is
    // what "one screen down" is measured in. React skips the re-render when
    // the answer hasn't changed, so this stays cheap.
    function update() {
      setShown(window.scrollY > window.innerHeight)
    }
    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [])

  if (!shown) return null

  function goToTop() {
    // matchMedia is missing in some test browsers; no answer means "smooth".
    const lessMotion =
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
    window.scrollTo({ top: 0, behavior: lessMotion ? 'auto' : 'smooth' })
    // preventScroll: focusing mustn't jump the page before the smooth scroll.
    focusTarget()?.focus({ preventScroll: true })
  }

  return (
    <button
      type="button"
      onClick={goToTop}
      className="fixed right-4 bottom-4 z-10 flex items-center gap-1 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-lg hover:bg-slate-700 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
    >
      <span aria-hidden="true">↑</span> Back to top
    </button>
  )
}
