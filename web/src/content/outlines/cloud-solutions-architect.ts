import type { Topic } from '../types.ts'

// The Cloud Solutions Architect track's outline-only topics, bundled as one
// piece that content.ts downloads only when something asks for this track:
// the map showing it, or one of its topics opening. Modules 1 (csa.linux.*),
// 2 (csa.hw.*) and 3 (csa.net.*) and their checkpoints have real content, or
// are being written, and are bundled into the app itself, so they're left out
// here (see LAZY_TRACKS in content.ts). The patterns must match the track's
// topic folders, which are named after their ids: csa.*
const files = import.meta.glob<Partial<Topic>>(
  [
    '../../../../content/topics/csa.*/topic.yaml',
    '!../../../../content/topics/csa.linux.*/topic.yaml',
    '!../../../../content/topics/csa.m1.checkpoint/topic.yaml',
    '!../../../../content/topics/csa.hw.*/topic.yaml',
    '!../../../../content/topics/csa.m2.checkpoint/topic.yaml',
    '!../../../../content/topics/csa.net.*/topic.yaml',
    '!../../../../content/topics/csa.m3.checkpoint/topic.yaml',
  ],
  { eager: true, import: 'default' },
)

export default Object.values(files)
