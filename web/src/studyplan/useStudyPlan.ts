import { useCallback, useState } from 'react'
import {
  clearStudyPlan,
  dismiss,
  loadStudyPlan,
  type StudyPlan,
  saveStudyPlan,
  wasDismissed,
} from './studyPlan.ts'

export type StudyPlanState = {
  /** The plan, if one was made on this device. */
  plan: StudyPlan | null
  /** False when the browser wouldn't keep the last plan saved. */
  kept: boolean
  /** Whether the learner said "Not now" to the question. */
  dismissed: boolean
  save: (plan: StudyPlan) => void
  forget: () => void
  notNow: () => void
}

/**
 * The study plan kept on this device (studyplan/studyPlan.ts), read once
 * when the page opens, and the ways to change it. Shared by the parts of a
 * page that show it, so saving it in one updates the others.
 */
export function useStudyPlan(): StudyPlanState {
  const [plan, setPlan] = useState<StudyPlan | null>(() => loadStudyPlan())
  const [kept, setKept] = useState(true)
  const [dismissed, setDismissed] = useState(() => wasDismissed())
  const save = useCallback((next: StudyPlan) => {
    setKept(saveStudyPlan(next))
    setPlan(next)
  }, [])
  const forget = useCallback(() => {
    clearStudyPlan()
    setKept(true)
    setPlan(null)
  }, [])
  const notNow = useCallback(() => {
    dismiss()
    setDismissed(true)
  }, [])
  return { plan, kept, dismissed, save, forget, notNow }
}
