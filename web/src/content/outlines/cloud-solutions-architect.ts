import type { Topic } from '../types.ts'

// The Cloud Solutions Architect track's topic outlines, bundled as one piece
// that content.ts downloads only when something asks for this track: the map
// showing it, or one of its topics opening. Every topic in the track is still
// an outline, so nothing else in the app needs them (see LAZY_TRACKS in
// content.ts). The pattern must match the track's topic folders, which are
// named after their ids: csa.*
const files = import.meta.glob<Partial<Topic>>(
  '../../../../content/topics/csa.*/topic.yaml',
  { eager: true, import: 'default' },
)

export default Object.values(files)
