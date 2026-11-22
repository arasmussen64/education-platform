import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { readingToReact } from './readingHtml.tsx'

function shown(html: string): HTMLElement {
  return render(<div>{readingToReact(html)}</div>).container
    .firstElementChild as HTMLElement
}

describe('a reading shown in the page (ADR-0031)', () => {
  it('rebuilds the plain parts of a page', () => {
    const box = shown(
      '<h3>Text</h3><p>A <strong>string</strong> is <code>str</code>.</p>' +
        '<pre><code>&gt;&gt;&gt; "a" + "b"\n\'ab\'</code></pre>' +
        '<ul>\n<li>one</li>\n<li>two</li>\n</ul>',
    )
    expect(box.querySelector('h3')).toHaveTextContent('Text')
    expect(box.querySelector('p')).toHaveTextContent('A string is str.')
    expect(box.querySelector('pre')?.textContent).toBe('>>> "a" + "b"\n\'ab\'')
    expect(box.querySelectorAll('li')).toHaveLength(2)
  })

  it('opens links beside the lesson, and only https ones', () => {
    const box = shown(
      '<p><a href="https://example.com/a">good</a> ' +
        '<a href="javascript:alert(1)">bad</a> ' +
        '<a href="/relative">local</a></p>',
    )
    const [good, bad, local] = box.querySelectorAll('a')
    expect(good).toHaveAttribute('href', 'https://example.com/a')
    expect(good).toHaveAttribute('target', '_blank')
    expect(good).toHaveAttribute('rel', 'noreferrer')
    expect(bad).not.toHaveAttribute('href')
    expect(local).not.toHaveAttribute('href')
  })

  it('leaves out anything that could run or style, with all it holds', () => {
    const box = shown(
      '<p onclick="steal()" style="color:red" class="x">kept</p>' +
        '<script>steal()</script><style>p{display:none}</style>' +
        '<iframe src="https://example.com"></iframe>' +
        '<div><p>inside something unknown</p></div>' +
        '<img src="https://example.com/a.png" onerror="steal()" alt="A chart">' +
        '<img src="data:image/png;base64,AAAA" alt="no">',
    )
    expect(box.querySelectorAll('script, style, iframe, div')).toHaveLength(0)
    const kept = box.querySelector('p')
    expect(kept).toHaveTextContent('kept')
    expect(kept?.attributes).toHaveLength(0)
    expect(box).not.toHaveTextContent('steal')
    expect(box).not.toHaveTextContent('inside something unknown')
    const images = box.querySelectorAll('img')
    expect(images).toHaveLength(1)
    expect(images[0]).toHaveAttribute('alt', 'A chart')
    expect(images[0]).toHaveAttribute('loading', 'lazy')
    expect(images[0]).not.toHaveAttribute('onerror')
  })

  it('keeps tables and formulas', () => {
    const box = shown(
      '<table>\n<thead>\n<tr><th colspan="2">Rate</th></tr>\n</thead>\n' +
        '<tbody><tr><td>5%</td><td>10%</td></tr></tbody></table>' +
        '<p><math display="block"><mfrac><mn>1</mn><mi>x</mi></mfrac></math></p>',
    )
    expect(box.querySelector('th')).toHaveAttribute('colspan', '2')
    expect(box.querySelectorAll('td')).toHaveLength(2)
    expect(box.querySelector('math')?.getAttribute('display')).toBe('block')
    expect(box.querySelector('mfrac')?.children).toHaveLength(2)
  })
})
