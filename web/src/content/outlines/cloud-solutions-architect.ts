import type { Topic } from '../types.ts'

// The Cloud Solutions Architect track's outline-only topics, bundled as one
// piece that content.ts downloads only when something asks for this track:
// the map showing it, or one of its topics opening. Module 1 (csa.linux.*)
// has real content and is bundled into the app itself, so it's left out
// here (see LAZY_TRACKS in content.ts). The patterns must match the track's
// topic folders, which are named after their ids: csa.*
const files = import.meta.glob<Partial<Topic>>(
  [
    '../../../../content/topics/csa.*/topic.yaml',
    '!../../../../content/topics/csa.linux.*/topic.yaml',
  ],
  { eager: true, import: 'default' },
)

export default Object.values(files)
