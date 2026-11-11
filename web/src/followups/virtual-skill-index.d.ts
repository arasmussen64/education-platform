// The module vite.config.ts builds from ../content (its skillIndex plugin).
// skillIndex.ts reads it as a SkillIndex.
declare module 'virtual:skill-index' {
  const index: Record<
    string,
    Record<
      string,
      {
        skills: string[]
        stage?: string
        test_skills?: Record<string, string[]>
      }
    >
  >
  export default index
}
