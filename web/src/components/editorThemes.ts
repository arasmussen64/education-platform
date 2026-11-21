// The code editor's two looks, in Momentum's colours (index.css): "morning
// trail" for light mode and "night trail" for dark mode. CodeEditor.tsx picks
// one by the same signal the rest of the app uses, the system's colour scheme.
//
// Lime is not used here: it means "forward" and nothing else. Syntax colours
// are few and earthy, and editorThemes.test.ts checks that each one keeps a
// contrast of at least 4.5 to 1 against the editor's background.
//
// CodeMirror wants plain hex values, so the background, text, gutter, cursor,
// line and comment colours below repeat named colours from index.css (card,
// ink, paper, muted, line and line-strong). tokens.test.ts fails if a copy
// here and its named colour stop being equal.

import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import type { Extension } from '@codemirror/state'
import { EditorView } from '@codemirror/view'
import { tags } from '@lezer/highlight'

/** The colours of one editor theme, as hex values. */
export type EditorPalette = {
  /** What the theme is called; the editor carries it as `data-theme`. */
  name: string
  dark: boolean
  /** Behind the code. */
  background: string
  /** Plain code: names, brackets, punctuation. */
  text: string
  /** The strip of line numbers. */
  gutter: string
  gutterText: string
  /**
   * A see-through tint over the line the cursor is on. See-through because
   * CodeMirror draws the selection underneath the lines: a solid colour here
   * would hide the selection on that line.
   */
  activeLine: string
  selection: string
  cursor: string
  /** The line between the gutter and the code, and around pop-ups. */
  line: string
  /** Syntax colours. Every one is checked against `background`. */
  syntax: {
    comment: string
    keyword: string
    string: string
    /** Numbers, True, False and None. */
    number: string
    /** The names of functions and classes where they are defined or called. */
    name: string
    operator: string
    /** Decorators, such as @property. */
    decorator: string
    /** Code the parser couldn't read. */
    invalid: string
  }
}

/** Light mode: pine ink on a near-white card, limestone gutter. */
export const MORNING_TRAIL: EditorPalette = {
  name: 'morning-trail',
  dark: false,
  background: '#fdfcf8',
  text: '#1b2620',
  gutter: '#f6f4ed',
  gutterText: '#666c5f',
  activeLine: '#1b26200a',
  selection: '#dedacb',
  cursor: '#1b2620',
  line: '#dedacb',
  syntax: {
    comment: '#666c5f',
    keyword: '#1d6b4a', // pine green
    string: '#96481c', // clay
    number: '#8b3a62', // berry
    name: '#1f5f8b', // lake blue
    operator: '#4f574c',
    decorator: '#5c6412', // moss
    invalid: '#b3261e',
  },
}

/** Dark mode: limestone text on the night-trail page colour. */
export const NIGHT_TRAIL: EditorPalette = {
  name: 'night-trail',
  dark: true,
  background: '#111914',
  text: '#edeae0',
  gutter: '#111914',
  gutterText: '#9a9a88',
  activeLine: '#edeae00f',
  selection: '#3b443b',
  cursor: '#edeae0',
  line: '#3b443b',
  syntax: {
    comment: '#9a9a88',
    keyword: '#8fcf9f', // sage
    string: '#e0b877', // sand
    number: '#e79ab5', // heather
    name: '#8cc4e8', // sky
    operator: '#c6c2b0',
    decorator: '#c9cf7a', // lichen
    invalid: '#ff9b8f',
  },
}

/** Which colour each kind of code gets. Anything not listed stays `text`. */
function highlightStyle({ syntax }: EditorPalette): HighlightStyle {
  return HighlightStyle.define([
    { tag: tags.comment, color: syntax.comment, fontStyle: 'italic' },
    { tag: tags.keyword, color: syntax.keyword },
    { tag: [tags.string, tags.special(tags.string)], color: syntax.string },
    { tag: [tags.number, tags.bool, tags.null], color: syntax.number },
    {
      tag: [
        tags.function(tags.variableName),
        tags.function(tags.propertyName),
        tags.className,
      ],
      color: syntax.name,
    },
    { tag: tags.operator, color: syntax.operator },
    { tag: tags.meta, color: syntax.decorator },
    { tag: tags.invalid, color: syntax.invalid },
  ])
}

/** Everything CodeMirror needs to draw the editor in one palette's colours. */
export function editorTheme(palette: EditorPalette): Extension {
  const popUp = {
    backgroundColor: palette.gutter,
    color: palette.text,
    border: `1px solid ${palette.line}`,
  }
  return [
    EditorView.theme(
      {
        '&': { color: palette.text, backgroundColor: palette.background },
        '.cm-content': { caretColor: palette.cursor },
        '.cm-cursor, .cm-dropCursor': { borderLeftColor: palette.cursor },
        // The long first selector is CodeMirror's own for a focused editor;
        // a shorter one would lose to its default selection colour.
        '&.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection':
          { backgroundColor: palette.selection },
        '.cm-activeLine': { backgroundColor: palette.activeLine },
        '.cm-gutters': {
          backgroundColor: palette.gutter,
          color: palette.gutterText,
          borderRight: `1px solid ${palette.line}`,
        },
        '.cm-activeLineGutter': {
          backgroundColor: palette.activeLine,
          color: palette.text,
        },
        // Two matching brackets are outlined, not filled, so the characters
        // keep their contrast.
        '&.cm-focused .cm-matchingBracket': {
          backgroundColor: 'transparent',
          outline: `1px solid ${palette.gutterText}`,
        },
        '.cm-selectionMatch': { backgroundColor: palette.selection },
        '.cm-foldPlaceholder': {
          backgroundColor: 'transparent',
          border: 'none',
          color: palette.gutterText,
        },
        '.cm-tooltip': popUp,
        '.cm-tooltip-autocomplete > ul > li[aria-selected]': {
          backgroundColor: palette.selection,
          color: palette.text,
        },
        '.cm-panels': popUp,
      },
      // Tells CodeMirror which of its own defaults (light or dark) to use
      // for anything this theme doesn't set.
      { dark: palette.dark },
    ),
    syntaxHighlighting(highlightStyle(palette)),
    EditorView.editorAttributes.of({ 'data-theme': palette.name }),
  ]
}

/** The palette for the system's colour scheme. */
export function paletteFor(dark: boolean): EditorPalette {
  return dark ? NIGHT_TRAIL : MORNING_TRAIL
}
