#!/usr/bin/env python3
"""
Reads content/articles/*.json and regenerates index.html, contributions.html,
and bibliography.html. Run locally or as part of the GitHub Actions ingest pipeline.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ARTICLES_DIR = Path('content/articles')
BLURBS_FILE  = Path('blurbs.md')


NAV = '''\
  <nav class="sitenav">
    <a href="/theory">Theory</a>
    <a href="/contributions">Contributions</a>
    <a href="/contributors">Contributors</a>
    <a href="/bibliography">Bibliography</a>
    <a href="/oracle">Oracle</a>
  </nav>'''


SORT_CONTROLS = '''\
  <div class="sort-controls">
    <span>Sort by</span>
    <button class="sort-btn active" data-sort="date">Date</button>
    <button class="sort-btn" data-sort="handle">Handle</button>
    <button class="sort-btn" data-sort="format">Format</button>
  </div>'''


SORT_SCRIPT = '''\
  <script>
    (function () {
      function sortBy(key) {
        var ul = document.querySelector('.articles');
        if (!ul) return;
        Array.from(ul.children).sort(function (a, b) {
          var av = a.dataset[key] || '', bv = b.dataset[key] || '';
          return key === 'date' ? bv.localeCompare(av) : av.localeCompare(bv);
        }).forEach(function (li) { ul.appendChild(li); });
        document.querySelectorAll('.sort-btn').forEach(function (btn) {
          btn.classList.toggle('active', btn.dataset.sort === key);
        });
      }
      document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.sort-btn').forEach(function (btn) {
          btn.addEventListener('click', function () { sortBy(btn.dataset.sort); });
        });
      });
    })();
  </script>'''


def load_articles():
    if not ARTICLES_DIR.exists():
        return []
    articles = []
    for p in ARTICLES_DIR.glob('*.json'):
        with open(p, encoding='utf-8') as f:
            articles.append(json.load(f))
    return articles


def index_items(articles):
    """Third-party resources shown on the front page (not books)."""
    items = [a for a in articles
             if a.get('type', 'resource') == 'resource' and a.get('format', 'essay') != 'book']
    items.sort(key=lambda a: a.get('submitted_at', ''), reverse=True)
    return items


def contribution_items(articles):
    """Original work by project contributors (not books)."""
    items = [a for a in articles
             if a.get('type') == 'contribution' and a.get('format', 'essay') != 'book']
    items.sort(key=lambda a: a.get('submitted_at', ''), reverse=True)
    return items


def books(articles):
    """Bibliography: resource books read by the book club."""
    items = [a for a in articles if a.get('format') == 'book']
    section_order = ['2026', '2026 side quest', '2025', '2025 side quest']
    items.sort(key=lambda a: (
        section_order.index(a.get('section', '2025')) if a.get('section') in section_order else 99,
        a.get('title', '')
    ))
    return items


def render_blurb():
    if not BLURBS_FILE.exists():
        return ''
    text = BLURBS_FILE.read_text(encoding='utf-8').strip()
    paras = []
    for para in text.split('\n\n'):
        para = para.strip()
        if not para:
            continue
        para = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', para)
        para = re.sub(r'\[([^\]]+)\](?!\()', lambda m: f'<a href="/{m.group(1).lower()}">{m.group(1)}</a>', para)
        para = re.sub(r'_([^_]+)_', r'<em>\1</em>', para)
        paras.append(f'    <p>{para}</p>')
    return '\n'.join(paras)


def fmt_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
        return dt.strftime('%-d %B %Y')
    except Exception:
        return iso[:10]


def escape(s):
    if s is None:
        return ''
    return (s
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;'))


def render_item(a):
    title = escape(a.get('title') or a.get('url') or 'Untitled')
    url   = escape(a.get('url') or '')
    by    = escape(a.get('handle') or a.get('submitted_by', ''))
    type_ = a.get('type', 'resource')
    fmt   = a.get('format', 'essay')
    badge_class = 'badge-contribution' if type_ == 'contribution' else 'badge-resource'
    badge_label = fmt.title()
    date        = fmt_date(a.get('submitted_at', ''))
    desc        = a.get('description') or ''
    title_html  = f'<a href="{url}">{title}</a>' if url else title
    desc_html   = f'\n      <p class="article-description">{escape(desc)}</p>' if desc else ''
    raw_date    = escape(a.get('submitted_at', ''))
    raw_handle  = escape(a.get('handle') or '')
    raw_fmt     = escape(fmt)
    return f'''\
    <li class="article" data-date="{raw_date}" data-handle="{raw_handle}" data-format="{raw_fmt}">
      <div class="article-meta">
        <span class="badge {badge_class}">{badge_label}</span>
        <span>{date}</span>
        <span>· {by}</span>
      </div>
      <h2 class="article-title">{title_html}</h2>{desc_html}
    </li>'''


def article_section(items, empty_msg):
    if not items:
        return f'  <p class="empty-state">{empty_msg}</p>', ''
    rows = '\n'.join(render_item(a) for a in items)
    body = f'{SORT_CONTROLS}\n  <ul class="articles">\n{rows}\n  </ul>'
    return body, SORT_SCRIPT


def page_shell(title, head_title, body_content, script='', comment=''):
    built = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    comment_line = f'  <!-- built: {built}{(" — " + comment) if comment else ""} -->\n'
    return f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — World Machines</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1><a href="/" style="color:inherit">World Machines</a></h1>
    <a href="/submit" class="submit-link">Submit</a>
  </header>
{NAV}
  <main>
{body_content}
  </main>
{script}{comment_line}</body>
</html>
'''


def build_index(articles):
    items = index_items(articles)
    resources_blurb = '''\
  <section class="blurb">
    <p>Third-party essays, articles, and other resources relevant to World Machines theory, submitted by <a href="/contributors">project contributors</a>. For original work by contributors, see <a href="/contributions">Contributions</a>.</p>
  </section>
'''
    content_body, script = article_section(items, 'No resources yet.')
    body = f'{resources_blurb}  <section class="articles-section">\n{content_body}\n  </section>'
    html = page_shell('Resources', 'Resources', body, script=script, comment=f'{len(items)} resources')
    # Front page has no subtitle
    html = html.replace('<title>Resources — World Machines</title>', '<title>World Machines</title>')
    # Header h1 has no link on the home page
    html = html.replace('<h1><a href="/" style="color:inherit">World Machines</a></h1>', '<h1>World Machines</h1>')
    Path('index.html').write_text(html, encoding='utf-8')
    print(f'Built index.html — {len(items)} resource(s)')


def build_contributions(articles):
    items = contribution_items(articles)
    blurb = render_blurb()
    blurb_section = f'  <section class="blurb">\n{blurb}\n  </section>\n' if blurb else ''
    content_body, script = article_section(items, 'No contributions yet.')
    body = f'{blurb_section}  <section class="articles-section">\n{content_body}\n  </section>'
    html = page_shell('Contributions', 'Contributions', body, script=script, comment=f'{len(items)} contributions')
    Path('contributions.html').write_text(html, encoding='utf-8')
    print(f'Built contributions.html — {len(items)} contribution(s)')


SECTION_LABELS = {
    '2026':            '2026 — Main Selections',
    '2026 side quest': '2026 — Side Quests',
    '2025':            '2025 — Main Selections',
    '2025 side quest': '2025 — Side Quests',
}


def build_bibliography(articles):
    items = books(articles)

    sections_html = []
    current_section = None
    for a in items:
        section = a.get('section', '')
        if section != current_section:
            if current_section is not None:
                sections_html.append('  </ul>')
            label = SECTION_LABELS.get(section, section)
            sections_html.append(f'  <h2 class="bib-section">{escape(label)}</h2>')
            sections_html.append('  <ul class="bib-list">')
            current_section = section
        title  = escape(a.get('title', ''))
        author = escape(a.get('author', ''))
        sections_html.append(f'''\
    <li class="bib-item">
      <span class="bib-title">{title}</span>
      <span class="bib-author">{author}</span>
    </li>''')
    if current_section is not None:
        sections_html.append('  </ul>')

    bib_body = '\n'.join(sections_html) if sections_html else '  <p class="empty-state">No books yet.</p>'
    body = f'''  <div class="blurb">
    <p>Books read by the Contraptions Book Club that inform the World Machines project, organised by year.</p>
  </div>
{bib_body}'''

    built = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    html = f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bibliography — World Machines</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1><a href="/" style="color:inherit">World Machines</a></h1>
    <a href="/submit" class="submit-link">Submit</a>
  </header>
{NAV}
  <main class="bib-main">
{body}
  </main>
  <!-- built: {built} ({len(items)} books) -->
</body>
</html>
'''
    Path('bibliography.html').write_text(html, encoding='utf-8')
    print(f'Built bibliography.html — {len(items)} book(s)')


def build():
    articles = load_articles()
    build_index(articles)
    build_contributions(articles)
    build_bibliography(articles)


if __name__ == '__main__':
    build()
