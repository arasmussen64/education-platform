import type { Topic } from '../types.ts'

// The Cloud Solutions Architect track's outline-only topics, bundled as one
// piece that content.ts downloads only when something asks for this track:
// the map showing it, or one of its topics opening. Module 1 (csa.linux.*)
// and its checkpoint (csa.m1.checkpoint) have real content and are bundled
// into the app itself, so they're left out here (see LAZY_TRACKS in
// content.ts). The patterns must match the track's topic folders, which are
// named after their ids: csa.*
const files = import.meta.glob<Partial<Topic>>(
  [
    '../../../../content/topics/csa.*/topic.yaml',
    '!../../../../content/topics/csa.linux.*/topic.yaml',
    '!../../../../content/topics/csa.m1.checkpoint/topic.yaml',
  ],
  { eager: true, import: 'default' },
)

export default Object.values(files)
