from pathlib import Path
import re, html, json, shutil

root = Path(__file__).resolve().parent
out = root / 'docs'
src = root / 'source'
esc = html.escape

out.mkdir(exist_ok=True)
(out / 'assets').mkdir(exist_ok=True)

shutil.copy(src / 'styles.css', out / 'styles.css')
shutil.copy(src / 'portrait.jpg', out / 'assets/portrait.jpg')

text = (src / 'records.txt').read_text(encoding='utf-8-sig') if (src / 'records.txt').exists() else ''
records = []
section = ''
group = ''
current = None

for line in text.splitlines():
    s = line.strip()
    if re.match(r'^[A-G]\. ', s):
        section = s[0]
        group = s[3:]
        current = None
        continue
    if s.startswith('•') or s in ['Reviste ISI:', 'Conferințe ISI:', 'Reviste BDI:', 'Conferințe BDI:', 'membru în echipă:']:
        if s == 'membru în echipă:':
            group = 'Membru în echipă'
            current = None
            continue
        group = s.lstrip('• ').rstrip(':')
        current = None
        continue
    m = re.match(r'^\d+\.\s*(.*)', s)
    if m:
        current = {'section': section, 'category': group, 'text': m[1]}
        records.append(current)
    elif current and s and not s.startswith(('Data:', 'Semnătura:')):
        current['text'] += ' ' + s

pubs = [r for r in records if r['section'] in ['B', 'C']]
for r in pubs:
    years = re.findall(r'\b(?:19|20)\d{2}\b', r['text'])
    r['year'] = years[0] if years else ''
    r['category'] = ({'internaționale': 'Capitole internaționale', 'naționale': 'Cărți naționale'}.get(r['category'], r['category']))

if (src / 'cnatdcu-additions.json').exists():
    pubs.extend(json.loads((src / 'cnatdcu-additions.json').read_text(encoding='utf-8-sig')))

projects = [r for r in records if r['section'] == 'E']
awards = [r for r in records if r['section'] == 'F']

(out / 'data').mkdir(exist_ok=True)
(out / 'data/publications.json').write_text(json.dumps(pubs, ensure_ascii=False, indent=2), encoding='utf-8')
(root / 'data.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')

nav = [
    ('index', 'Acasă'),
    ('research', 'Cercetare'),
    ('publications', 'Publicații'),
    ('teaching', 'Educație'),
    ('about', 'Profil'),
    ('contact', 'Contact')
]

profiles = (
    '<a href="https://orcid.org/0009-0009-9186-3488">ORCID ↗</a>'
    '<a href="https://www.linkedin.com/in/mihai-anescu-289b83214/">LinkedIn ↗</a>'
)

def page(key, title, body):
    links = ''.join(
        f'<a href="{k}.html" ' + ('aria-current="page"' if k == key else '') + f'>{v}</a>'
        for k, v in nav
    )
    (out / f'{key}.html').write_text(f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="index,follow"><title>{title} | Mihai ANESCU</title><meta name="description" content="Profilul academic al drd. ing. Mihai ANESCU: cercetare și publicații în inginerie electrică la Universitatea Națională de Știință și Tehnologie POLITEHNICA București."><link rel="stylesheet" href="styles.css"><script defer src="app.js"></script></head><body><a class="skip" href="#main">Salt la conținut</a><header class="header"><div class="wrap header-inner"><a class="brand" href="index.html"><span class="monogram">MA</span><span class="brand-name">Mihai ANESCU<small>Cercetare &amp; profil academic</small></span></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Meniu</button><nav id="navigation" class="nav" aria-label="Navigare principală">{links}</nav></div></header><main id="main">{body}</main><footer class="footer"><div class="wrap"><div class="footer-top"><div><strong>Mihai ANESCU</strong><br>Inginerie electrică · POLITEHNICA București</div><nav aria-label="Profiluri academice">{profiles}<a href="cv.html">Curriculum vitae</a></nav></div><div class="footer-bottom"><span>© 2026 Mihai ANESCU · București, România</span><span>Conținut: Profil academic și lista lucrărilor științifice actualizate în 2026</span></div></div></footer></body></html>""", encoding='utf-8')

def intro(title, desc='', tag='Profil academic'):
    lead_html = f'<p class="lead">{desc}</p>' if desc else ''
    return f'<div class="wrap page-intro"><p class="eyebrow">{tag}</p><h1>{title}</h1>{lead_html}</div>'

def rows(items):
    return ''.join(
        f'<article class="timeline-row"><div class="date">{esc(a)}</div><div><h3>{esc(b)}</h3><p>{esc(c)}</p></div></article>'
        for a, b, c in items
    )

def pubrow(r, i):
    d = re.search(r'10\.\d{4,9}/[A-Za-z0-9./_()\-]+', r['text'])
    link = f'<a href="https://doi.org/{d[0].rstrip(".,;")}">DOI / Editor ↗</a>' if d else ''
    return f'<article class="pub-row" data-search="{esc(r["text"], quote=True)}" data-year="{r["year"]}" data-type="{esc(r["category"], quote=True)}"><div class="pub-year">{r["year"]}</div><div><div class="pub-meta">{esc(r["category"])}</div><p class="citation">{esc(r["text"])}</p><div class="pub-actions">{link}</div></div></article>'

# 1. Home Page (index.html)
page('index', 'Acasă', f"""<div class="wrap"><section class="hero"><div><p class="eyebrow">Inginerie electrică · Cercetare · Educație</p><h1>Mihai<br>ANESCU</h1><p class="position">stud. Doctorand</p><div class="buttons"><a class="button" href="research.html">Explorează cercetarea →</a><a class="button secondary" href="publications.html">Vezi publicațiile</a></div><div class="profile-links">{profiles}</div></div><div class="hero-portrait"><figure><img src="assets/portrait.jpg" width="368" height="368" alt="Mihai ANESCU, student doctorand la Facultatea de Inginerie Electrică"><figcaption class="portrait-caption"><span>Facultatea de Inginerie Electrică</span><span>060042, București, România</span></figcaption></figure></div></section><div class="metrics"><div class="metric"><strong>{len(pubs)}</strong><span>Înregistrări bibliografice</span></div><div class="metric"><strong>{len(projects)}</strong><span>Proiecte de cercetare</span></div></div></div>""")

# 2. About Page (about.html)
career = []
edu = []
awards_html = ('<h2>Premii și distincții</h2>' + ''.join('<p>' + esc(r['text']) + '</p>' for r in awards)) if awards else ''
page('about', 'Profil', intro('Profil academic', '') + f'<section class="section wrap"><a class="button secondary" href="publications.html">Vezi publicațiile</a>{rows(career)}{rows(edu)}{awards_html}</section>')

# 3. Research Page (research.html)
# Note: Keeping project-layout.py disabled by default so Prof. Seritan's projects don't overwrite your clean research page.
# Uncomment the exec() line below only after cleaning source/project-layout.py.
# if (src / 'project-layout.py').exists(): exec((src / 'project-layout.py').read_text(encoding='utf-8-sig'))
projects_html = ''.join(f'<article class="project-entry"><div class="pub-meta">{esc(r["category"])}</div><p>{esc(r["text"])}</p></article>' for r in projects) if projects else '<p class="empty">Nu există proiecte înregistrate.</p>'
page('research', 'Cercetare', intro('Cercetare', '') + f'<section class="section wrap" id="projects"><h2>Proiecte de cercetare</h2>{projects_html}</section>')

# 4. Publications Page (publications.html)
options = lambda values: ''.join(f'<option>{esc(v)}</option>' for v in values)
page('publications', 'Publicații', intro('Publicații', '') + f'<section class="wrap section"><form class="filters" data-filter-form><label class="search-field">Caută după titlu, autor sau cuvânt-cheie<input type="search" placeholder="Caută..."></label><label>An<select name="year"><option value="">Toți anii</option>{options(sorted(set(r["year"] for r in pubs if r["year"]), reverse=True))}</select></label><label>Categorie<select name="type"><option value="">Toate categoriile</option>{options(list(dict.fromkeys(r["category"] for r in pubs)))}</select></label><button type="button" class="button secondary" data-reset>Resetează</button></form><div class="filter-count"><span data-result-count aria-live="polite">{len(pubs)} înregistrări</span><a href="data/publications.json" download>Descarcă datele (JSON)</a></div><div class="pub-list">' + ''.join(pubrow(r, i) for i, r in enumerate(pubs)) + '</div><p class="empty" data-empty hidden>Nicio lucrare nu corespunde filtrelor. Încercați alt termen sau resetați filtrele.</p></section>')

# 5. Teaching Page (teaching.html)
courses = []
page('teaching', 'Educație', intro('Educație & îndrumare', '') + '<section class="section wrap"><div class="course-list">' + ''.join(f'<article class="course"><h3>{a}</h3><p>{b}</p></article>' for a, b in courses) + '</div></section>')

# 6. CV Page (cv.html)
page('cv', 'Curriculum vitae', intro('Curriculum vitae', 'Sinteză profesională · Mihai ANESCU') + '<section class="section wrap"><button class="button secondary" data-print>Tipărește / Salvează PDF</button><div class="prose section"><p>stud. Doctorand · Facultatea de Inginerie Electrică · Universitatea Națională de Știință și Tehnologie POLITEHNICA București<br>mihai.anescu0811@stud.electro.upb.ro · ORCID 0009-0009-9186-3488</p>' + rows(career) + rows(edu) + '<a href="publications.html">Consultați catalogul publicațiilor →</a></div></section>')

# 7. Contact Page (contact.html)
page('contact', 'Contact', intro('Să colaborăm.', 'Pentru colaborări de cercetare, proiecte academice și discuții privind formarea în inginerie electrică.') + f'<section class="section wrap contact-grid"><div><article class="contact-card"><h2>E-mail universitar</h2><a href="mailto:mihai.anescu0811@stud.electro.upb.ro">mihai.anescu0811@stud.electro.upb.ro</a></article><article class="contact-card"><h2>Afiliere</h2><p>Facultatea de Inginerie Electrică<br>Universitatea Națională de Știință și Tehnologie POLITEHNICA București</p><p>Splaiul Independenței nr. 314<br>060042, București, România</p></article></div><div><article class="contact-card"><h2>Identificatori academici</h2><p>ORCID: <a href="https://orcid.org/0009-0009-9186-3488">0009-0009-9186-3488</a></p></article><article class="contact-card"><h2>Profil profesional</h2><p><strong>ing.</strong></p><a class="button secondary" href="assets/CV_MihaiAnescu-1.pdf" download>Download CV (PDF, Romanian)</a><div class="profile-links">{profiles}</div></article></div></section>')

if (src / 'app.js').exists():
    js = (src / 'app.js').read_text(encoding='utf-8-sig').replace("'Close':'Menu'", "'Închide':'Meniu'").replace("menu.textContent='Menu'", "menu.textContent='Meniu'").replace("`${count} of ${cards.length} ${filterForm.dataset.noun||'publications'}`", "`${count} din ${cards.length} înregistrări`")
    (out / 'app.js').write_text(js, encoding='utf-8')

with (out / 'styles.css').open('a', encoding='utf-8') as f:
    f.write('\n.citation{margin:10px 0;overflow-wrap:anywhere}.project-entry{padding:22px 0;border-bottom:1px solid var(--line);overflow-wrap:anywhere}.project-entry p{margin:0}.section>h2{margin-top:45px}.hero-portrait{max-width:420px}.nav{gap:20px}@media print{.header,.footer,button{display:none!important}.section{padding:20px 0}.wrap{width:100%}.timeline-row{break-inside:avoid}}')

print('Publications:', len(pubs), 'Projects:', len(projects))

# Note: translate-en.py is commented out below so it does not re-inject Prof. Seritan's English profile data.
# Uncomment once source/translate-en.py is updated.
# if (src / 'translate-en.py').exists(): exec((src / 'translate-en.py').read_text(encoding='utf-8-sig'))
