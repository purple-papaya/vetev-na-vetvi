#!/usr/bin/env python3
"""SEO and LLM metadata for Větev na větvi. Standard library only.

Run from the repository root after adding or changing a page:

    python3 tools/seo.py

What it does:
  * writes a managed block into the <head> of every page listed in PAGES: title, description,
    canonical URL, robots, Open Graph and Twitter card, and JSON-LD structured data
    (WebSite, CollectionPage, Article + LearningResource with citations, FAQPage, BlogPosting,
    BreadcrumbList). The block sits between the "seo:begin" and "seo:end" comments.
  * writes sitemap.xml, robots.txt, llms.txt and llms-full.txt to the repository root.

Titles, descriptions and topics live in PAGES below. FAQs, sources and reading time are read
from the page itself, dates from git history (commits whose message starts with "SEO:" are
ignored, so metadata-only changes do not count as content updates).
"""
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = 'https://vetevnavetvi.cz/'   # change here if the site ever moves
SITE_NAME = 'Větev na větvi'
SITE_DESC = ('Český terénní zápisník o biologii těla: trpělivé výklady metabolismu, nervů, fyziologie, léků, genů, '
             'imunity, vývoje a hormonů s interaktivními simulacemi a ověřenými zdroji.')
SITE_DESC_EN = ('A Czech-language field guide to the biology of the human body: patient, source-checked explanations '
                'of metabolism, neurons, physiology, drugs, genes, immunity, development and hormones, each chapter '
                'with interactive simulations.')
DEFAULT_IMAGE = 'assets/og/vetev-na-vetvi.jpg'
LOGO_IMAGE = 'assets/og/logo.png'
THEME_COLOR = '#2F5D46'
WPM = 200   # reading speed used for timeRequired

# kind: home | hub | branch | chapter | blog | post | stub | 404
PAGES = {
    'index.html': dict(
        kind='home', title='Větev na větvi – terénní zápisník o biologii těla',
        desc='Biologie, která tě pohání, vysvětlená pomalu a bez zjednodušování: kapitoly o metabolismu, nervech, '
             'imunitě, hormonech a dalším, s interaktivními simulacemi.'),
    'pages/wetware.html': dict(
        kind='hub', name='Wetware', title='Wetware – interaktivní průvodce biologií těla | Větev na větvi',
        desc='Osm větví biologie těla, od biochemie a neurobiologie po imunologii a endokrinologii. Každá s první '
             'kapitolou, simulacemi a zdroji.'),
    # ---- branches
    'pages/wetware-biochemie.html': dict(
        kind='branch', name='Biochemie', title='Biochemie – Wetware | Větev na větvi',
        desc='Chemie života: energie, molekuly a reakce. První kapitola Jsi sloveso vysvětluje metabolismus, ATP '
             'a zpětné vazby se simulacemi.'),
    'pages/wetware-neurobiologie.html': dict(
        kind='branch', name='Neurobiologie', title='Neurobiologie – Wetware | Větev na větvi',
        desc='Nervy, signály a to, jak se z 86 miliard neuronů vynoří já. První kapitola: klidový potenciál, práh, '
             'akční potenciál a synapse.'),
    'pages/wetware-fyziologie.html': dict(
        kind='branch', name='Fyziologie', title='Fyziologie – Wetware | Větev na větvi',
        desc='Jak spolu orgány a soustavy spolupracují. První kapitola Moře pod kůží: zpětná vazba, spády a pumpy, '
             'proudění, povrchy a obnova.'),
    'pages/wetware-farmakologie.html': dict(
        kind='branch', name='Farmakologie', title='Farmakologie – Wetware | Větev na větvi',
        desc='Léky jako vlna v krvi. První kapitola Lék je vlna: farmakokinetika a farmakodynamika, poločas, '
             'ustálený stav a terapeutické okno.'),
    'pages/wetware-molekularni-biologie.html': dict(
        kind='branch', name='Molekulární biologie', title='Molekulární biologie – Wetware | Větev na větvi',
        desc='DNA, RNA a bílkoviny bez zjednodušování. První kapitola Čtení bez čtenáře: opis s korekturou, '
             'genetický kód, mutace a přepínače genů.'),
    'pages/wetware-imunologie.html': dict(
        kind='branch', name='Imunologie', title='Imunologie – Wetware | Větev na větvi',
        desc='Jak tělo pozná vetřelce, kterého nikdy nevidělo. První kapitola: vrozená imunita, V(D)J '
             'rekombinace, výběr v brzlíku a imunitní paměť.'),
    'pages/wetware-vyvojova-biologie.html': dict(
        kind='branch', name='Vývojová biologie', title='Vývojová biologie – Wetware | Větev na větvi',
        desc='Jak z jediné buňky vyroste tělo bez plánku. První kapitola: morfogeny a prahy, Notch–Delta, '
             'segmentační hodiny a řízená buněčná smrt.'),
    'pages/wetware-endokrinologie.html': dict(
        kind='branch', name='Endokrinologie', title='Endokrinologie – Wetware | Větev na větvi',
        desc='Hormony jako zprávy pro celé tělo. První kapitola Dopis pro všechny: receptory, zpětná vazba štítné '
             'žlázy, poločasy a pulzy hormonů.'),
    # ---- chapters
    'pages/wetware-ch1-jsi-sloveso.html': dict(
        kind='chapter', branch='pages/wetware-biochemie.html', name='Jsi sloveso',
        title='Jsi sloveso: úvod do metabolismu | Větev na větvi',
        desc='Proč jsi spíš děj než věc: metabolismus jako pomalý řízený oheň, ATP, energie po schodech a zpětné '
             'vazby bez ředitele. Se třemi simulacemi.',
        about=['metabolismus', 'ATP', 'enzymy', 'aktivační energie', 'zpětnovazebná inhibice', 'ustálený stav'],
        en='Introduction to metabolism: why you are a process rather than a thing; ATP, stepwise release of energy '
           'and feedback inhibition without a central controller.'),
    'pages/wetware-neurobiologie-ch1-jak-se-sul-naucila-rikat-ja.html': dict(
        kind='chapter', branch='pages/wetware-neurobiologie.html', name='Jak se sůl naučila říkat já',
        title='Jak se sůl naučila říkat já: úvod do neurobiologie | Větev na větvi',
        desc='Jak z iontů soli vznikne myšlenka: klidový potenciál a sodno-draselná pumpa, práh a akční potenciál, '
             'synapse a 86 miliard neuronů. S pěti simulacemi.',
        about=['neuron', 'klidový membránový potenciál', 'sodno-draselná pumpa', 'akční potenciál', 'synapse',
               'myelin'],
        en='Introduction to neurobiology: resting potential and the sodium-potassium pump, threshold and the '
           'action potential, myelin, synapses and 86 billion neurons.'),
    'pages/wetware-fyziologie-ch1-more-pod-kuzi.html': dict(
        kind='chapter', branch='pages/wetware-fyziologie.html', name='Moře pod kůží',
        title='Moře pod kůží: úvod do fyziologie | Větev na větvi',
        desc='Jak tělo drží vnitřní prostředí stálé: negativní zpětná vazba, spády a pumpy, proudění, poskládané '
             'povrchy a obnova buněk. S pěti simulacemi.',
        about=['homeostáza', 'negativní zpětná vazba', 'difuze', 'osmóza', 'ustálený stav', 'obnova buněk'],
        en='Introduction to physiology: homeostasis as a steady state rather than equilibrium, negative feedback, '
           'diffusion and pumps, flow, folded surfaces and cell turnover.'),
    'pages/wetware-farmakologie-ch1-lek-je-vlna.html': dict(
        kind='chapter', branch='pages/wetware-farmakologie.html', name='Lék je vlna',
        title='Lék je vlna: farmakokinetika a farmakodynamika | Větev na větvi',
        desc='Proč se lék bere dvakrát denně: koncentrace v čase, poločas a ustálený stav, receptory, potence '
             'a účinnost, terapeutické okno. Se čtyřmi simulacemi.',
        about=['farmakokinetika', 'farmakodynamika', 'biologický poločas', 'ustálený stav', 'terapeutické okno',
               'receptor'],
        en='Introduction to pharmacokinetics and pharmacodynamics: the concentration-time curve, half-life and '
           'steady state, receptors, potency and efficacy, and the therapeutic window.'),
    'pages/wetware-molekularni-biologie-ch1-cteni-bez-ctenare.html': dict(
        kind='chapter', branch='pages/wetware-molekularni-biologie.html', name='Čtení bez čtenáře',
        title='Čtení bez čtenáře: úvod do molekulární biologie | Větev na větvi',
        desc='Jak se z DNA stane tělo, když v buňce nikdo nečte: opis s korekturou, mRNA a bílkoviny, genetický '
             'kód a mutace, přepínače genů. Se čtyřmi simulacemi.',
        about=['DNA', 'replikace DNA', 'transkripce', 'translace', 'genetický kód', 'mutace', 'regulace genů'],
        en='Introduction to molecular biology: DNA replication with proofreading, mRNA and protein turnover, the '
           'genetic code and mutations, and gene switches (the eve stripe in fruit flies).'),
    'pages/wetware-imunologie-ch1-darwin-v-mizni-uzline.html': dict(
        kind='chapter', branch='pages/wetware-imunologie.html', name='Darwin v mízní uzlině',
        title='Darwin v mízní uzlině: jak funguje imunita | Větev na větvi',
        desc='Jak tělo pozná vetřelce, kterého nikdy nevidělo: receptory pro vzory, V(D)J rekombinace, výběr '
             'v brzlíku, zárodečná centra a paměť. Se čtyřmi simulacemi.',
        about=['imunitní systém', 'vrozená imunita', 'V(D)J rekombinace', 'brzlík', 'klonální selekce',
               'afinitní maturace', 'imunologická paměť'],
        en='Introduction to immunology: pattern recognition, V(D)J recombination, thymic selection, clonal '
           'selection and affinity maturation in germinal centres, and immune memory.'),
    'pages/wetware-vyvojova-biologie-ch1-telo-ktere-se-postavilo-samo.html': dict(
        kind='chapter', branch='pages/wetware-vyvojova-biologie.html', name='Tělo, které se postavilo samo',
        title='Tělo, které se postavilo samo: vývojová biologie | Větev na větvi',
        desc='Jak z jediné buňky vyroste tělo bez plánku: morfogeny a prahy, boční inhibice Notch–Delta, '
             'segmentační hodiny a řízená buněčná smrt. Se čtyřmi simulacemi.',
        about=['vývojová biologie', 'morfogen', 'boční inhibice', 'Notch–Delta', 'somitogeneze', 'apoptóza'],
        en='Introduction to developmental biology: morphogen gradients and thresholds, Delta-Notch lateral '
           'inhibition, the segmentation clock and wavefront, and programmed cell death.'),
    'pages/wetware-endokrinologie-ch1-dopis-pro-vsechny.html': dict(
        kind='chapter', branch='pages/wetware-endokrinologie.html', name='Dopis pro všechny',
        title='Dopis pro všechny: jak fungují hormony | Větev na větvi',
        desc='Hormony jako zprávy pro celé tělo: receptory a afinita, zpětná vazba štítné žlázy, poločasy, denní '
             'rytmus kortizolu a pulzy GnRH. Se čtyřmi simulacemi.',
        about=['hormony', 'endokrinní systém', 'receptor', 'zpětná vazba', 'štítná žláza', 'kortizol', 'GnRH'],
        en='Introduction to endocrinology: hormone concentrations and receptor affinity, the thyroid feedback '
           'loop, slow and fast hormones and half-lives, the cortisol rhythm and pulsatile GnRH.'),
    # ---- blog
    'pages/blog.html': dict(
        kind='blog', name='Blog', title='Blog | Větev na větvi',
        desc='Kratší texty mezi kapitolami Wetware: souvislosti napříč větvemi biologie, poznámky k psaní a to, co '
             'se do kapitol nevešlo.'),
    'pages/blog-spad-prah-smycka.html': dict(
        kind='post', name='Spád, práh, smyčka', date='2026-10-21',
        title='Spád, práh, smyčka: co spojuje biologii těla | Větev na větvi',
        desc='Co mají společného metabolismus, nervy, léky, geny, imunita, vývoj i hormony: spád, práh a smyčka. '
             'A nikde nikdo, kdo by to řídil.',
        about=['gradient', 'práh', 'zpětná vazba', 'ustálený stav', 'samoorganizace'],
        en='Essay: what all eight first chapters share. Gradients kept away from equilibrium, thresholds that '
           'turn them into decisions, feedback loops, and no central controller.'),
    # ---- placeholders, not worth indexing yet
    'pages/o-mne.html': dict(
        kind='about', name='O mně', title='O mně – Pája, autorka Větve na větvi',
        desc='Pája vystudovala molekulární biologii a biochemii a pracuje jako datová analytička v Brně. Jak vznikají '
             'kapitoly, z jakých učebnic a s jakou rolí AI.'),
    'pages/pribehy.html': dict(kind='stub', name='Příběhy', title='Příběhy | Větev na větvi',
                               desc='Beletrie, eseje a terénní poznámky. Stránka se připravuje.'),
    'pages/lusteni.html': dict(kind='stub', name='Luštění', title='Luštění | Větev na větvi',
                               desc='Šifry, hlavolamy a vzorce ke spatření. Stránka se připravuje.'),
    'pages/zpetna-vazba.html': dict(kind='stub', name='Zpětná vazba', title='Zpětná vazba | Větev na větvi',
                                    desc='Napiš, co ti sedlo, co skřípalo nebo kde je chyba. Stránka se připravuje.'),
    '404.html': dict(kind='404', name='Stránka nenalezena', title='Stránka nenalezena | Větev na větvi',
                     desc='Tahle adresa na webu Větev na větvi neexistuje.'),
}
INDEXABLE = {'home', 'hub', 'branch', 'chapter', 'blog', 'post', 'about'}

# The author, as described on the About page (pages/o-mne.html).
AUTHOR = dict(name='Pája', job='datová analytička', locality='Brno', country='CZ',
              education='Molekulární biologie a biochemie organismů',
              knows=['molekulární biologie', 'biochemie', 'fyziologie', 'datová analýza'])


# ------------------------------------------------------------------ helpers
def url_of(path):
    return SITE_URL if path == 'index.html' else SITE_URL + path


def git_dates(path):
    """(first, last) commit dates of a file, ignoring commits whose message starts with 'SEO:'."""
    try:
        out = subprocess.run(['git', 'log', '--follow', '--invert-grep', '--grep=^SEO:', '--format=%aI', '--', path],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        out = []
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return (out[-1] if out else now), (out[0] if out else now)


def text_of(fragment):
    t = re.sub(r'<(script|style|svg)\b.*?</\1>', ' ', fragment, flags=re.S | re.I)
    t = re.sub(r'<sup>(.*?)</sup>', r'^\1', t, flags=re.S)
    t = re.sub(r'<sub>(.*?)</sub>', r'_\1', t, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('\xa0', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return re.sub(r'\s+([,.;:!?)])', r'\1', t).replace('( ', '(')


def faqs_of(page_html):
    """Question/answer pairs from <details class="q"> or <details class="qa"> blocks."""
    out = []
    for m in re.finditer(r'<details class="qa?"[^>]*>(.*?)</details>', page_html, re.S):
        block = m.group(1)
        q = re.search(r'<summary>(.*?)</summary>', block, re.S)
        if not q:
            continue
        question = text_of(re.sub(r'<span class="qno">.*?</span>', '', q.group(1), flags=re.S))
        body = block[q.end():]
        body = re.sub(r'<p class="q-mini">.*?</p>', '', body, flags=re.S)
        answer = text_of(body)
        if question and answer:
            out.append((question, answer))
    return out


def sources_of(page_html):
    """Visible source list items of a chapter (the section headed 'Zdroje')."""
    m = re.search(r'<(section|div)[^>]*class="[^"]*sources[^"]*"[^>]*>(.*?)</\1>', page_html, re.S)
    if not m:
        i = page_html.find('Zdroje')
        if i < 0:
            return []
        m_ul = re.search(r'<ul[^>]*>(.*?)</ul>', page_html[i:], re.S)
        items = re.findall(r'<li[^>]*>(.*?)</li>', m_ul.group(1), re.S) if m_ul else []
    else:
        inner = re.sub(r'<h\d[^>]*>.*?</h\d>', '', m.group(2), flags=re.S)
        items = re.findall(r'<li[^>]*>(.*?)</li>', inner, re.S) or re.split(r'&nbsp;·&nbsp;|\s·\s', inner)
    out = [text_of(x) for x in items if text_of(x)]
    if not out:   # no sources section: collect the source notes attached to answers
        for note in re.findall(r'<(?:span|p) class="src">(.*?)</(?:span|p)>', page_html, re.S):
            note = re.sub(r'^(Zdroje?|Vychází z):\s*', '', text_of(note))
            out += [x.strip(' .') for x in note.split(';') if x.strip(' .')]
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


# ------------------------------------------------------------------ HTML -> Markdown (for llms-full.txt)

def strip_blocks(src, start_pattern):
    """Remove every element whose start tag matches start_pattern, including nested children."""
    while True:
        m = re.search(start_pattern, src)
        if not m:
            return src
        tag = re.match(r'<(\w+)', m.group(0)).group(1)
        depth, pos = 0, m.start()
        for t in re.finditer(r'<(/?)' + tag + r'\b[^>]*>', src[m.start():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                pos = m.start() + t.end()
                break
        else:
            pos = len(src)
        src = src[:m.start()] + ' ' + src[pos:]

class _Md(HTMLParser):
    BLOCKS = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li', 'dt', 'dd', 'summary', 'figcaption', 'aside', 'blockquote', 'tr'}
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, page_path):
        super().__init__(convert_charrefs=True)
        self.page_path, self.lines, self.buf, self.prefix, self.href = page_path, [], [], [], None
        self.pre = None

    def _flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
        t = re.sub(r'\s+([,.;:!?)])', r'\1', t).replace('( ', '(')
        if t:
            self.lines.append((self.prefix[-1] if self.prefix else '') + t)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'pre':
            self._flush()
            self.pre = []
            return
        if self.pre is not None:
            return
        if tag in self.VOID:
            if tag == 'br':
                self.buf.append(' ')
            return
        if tag in self.BLOCKS:
            self._flush()
            cls = a.get('class') or ''
            pre = {'h1': '# ', 'h2': '## ', 'h3': '### ', 'h4': '#### ', 'h5': '##### ', 'li': '- ', 'dt': '- ',
                   'dd': '  ', 'summary': '### ', 'figcaption': '', 'aside': '> ', 'blockquote': '> '}.get(tag, '')
            if tag == 'p' and self.prefix and self.prefix[-1] == '> ':
                pre = '> '
            if 'punch' in cls:
                pre = '**'
            self.prefix.append(pre)
        elif tag == 'sup':
            self.buf.append('^')
        elif tag == 'sub':
            self.buf.append('_')
        elif tag == 'a':
            href = a.get('href') or ''
            self.href = href if href and not href.startswith('#') else None
            if self.href:
                self.buf.append('[')
        elif tag == 'span' and 'num' in (a.get('class') or '').split():
            self.buf.append('')

    def handle_endtag(self, tag):
        if tag == 'pre' and self.pre is not None:
            code = ''.join(self.pre).strip('\n')
            self.lines.append('```\n' + code + '\n```')
            self.pre = None
            return
        if self.pre is not None:
            return
        if tag in self.BLOCKS:
            if self.prefix and self.prefix[-1] == '**':
                t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
                self.buf = [t + '**'] if t else []
            self._flush()
            if self.prefix:
                self.prefix.pop()
        elif tag == 'a' and self.href:
            target = self.href
            if not target.startswith(('http://', 'https://', 'mailto:')):
                base = url_of(self.page_path)
                target = re.sub(r'[^/]*$', '', base) + target if not target.startswith('../') else \
                    re.sub(r'[^/]*/[^/]*$', '', base) + target[3:]
            self.buf.append('](' + target + ')')
            self.href = None
        elif tag == 'span':
            pass

    def handle_data(self, data):
        if self.pre is not None:
            self.pre.append(data.replace('\xa0', ' '))
            return
        self.buf.append(data.replace('\xa0', ' '))

    def markdown(self):
        self._flush()
        out, prev = [], ''
        for line in self.lines:
            if line.startswith('- ') and prev.startswith('- '):
                out.append(line)
            else:
                out.extend(['', line])
            prev = line
        return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip() + '\n'


def markdown_of(page_path, page_html):
    body = page_html[page_html.find('<body'):]
    body = re.sub(r'<(script|style|svg|canvas|nav|button|select|template|noscript)\b.*?</\1>', ' ', body, flags=re.S | re.I)
    body = re.sub(r'<(header|footer)\b.*?</\1>', ' ', body, flags=re.S | re.I)
    body = re.sub(r'<label\b.*?</label>|<input\b[^>]*>', ' ', body, flags=re.S | re.I)
    body = re.sub(r'<div class="rule"[^>]*>.*?</div>', ' ', body, flags=re.S)
    body = strip_blocks(body, r'<div class="topbar"[^>]*>')
    body = re.sub(r'<p class="(sign|signoff)">.*?</p>', ' ', body, flags=re.S)
    body = re.sub(r'<aside class="codenote">\s*<div class="bar"><span class="lbl">(.*?)</span>.*?</div>\s*<pre>(.*?)</pre>\s*</aside>',
                  lambda m: '<pre>' + m.group(2).replace(r'# ', '# ', 1) + '</pre>', body, flags=re.S)
    body = re.sub(r'<span class="k">(.*?)</span>', r' – \1', body, flags=re.S)

    def fig(m):   # keep only the caption of figures (simulations, illustrations, branch art)
        cap = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', m.group(0), re.S)
        if not cap:
            return ' '
        label = 'Simulace' if re.search(r'class="sim\b', m.group(0)) else 'Obrázek'
        return f'<p>{label}: {cap.group(1)}</p>'

    def triad(m):
        items = []
        for card in re.findall(r'<div class="card">(.*?)</div>', m.group(0), re.S):
            br = text_of((re.search(r'<span class="br">(.*?)</span>', card, re.S) or [None, ''])[1])
            h3 = re.search(r'<h3>(.*?)</h3>', card, re.S)
            moves = '; '.join(f'{text_of(dt)}: {text_of(dd)}' for dt, dd in
                              re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', card, re.S))
            items.append(f'<li>{h3.group(1) if h3 else ""} ({br}) – {moves}</li>')
        return '<ul>' + ''.join(items) + '</ul>'

    body = re.sub(r'<figure class="triad".*?</figure>', triad, body, flags=re.S)
    body = re.sub(r'<figure\b.*?</figure>', fig, body, flags=re.S)
    body = re.sub(r'<span class="qno">.*?</span>|<p class="q-mini">.*?</p>|<p class="sign">.*?</p>', ' ', body, flags=re.S)
    body = re.sub(r'<div class="tag">(.*?)</div>', lambda m: text_of(m.group(1)) + ': ', body, flags=re.S)
    body = re.sub(r'<span class="num">(.*?)</span>', r'\1. ', body, flags=re.S)
    p = _Md(page_path)
    p.feed(body)
    return p.markdown()


# ------------------------------------------------------------------ JSON-LD
ORG = {'@type': 'Organization', '@id': SITE_URL + '#org', 'name': SITE_NAME, 'url': SITE_URL,
       'logo': {'@type': 'ImageObject', 'url': SITE_URL + LOGO_IMAGE, 'width': 512, 'height': 512}}
PERSON_ID = SITE_URL + 'pages/o-mne.html#person'
PERSON = {'@type': 'Person', '@id': PERSON_ID, 'name': AUTHOR['name'], 'url': SITE_URL + 'pages/o-mne.html',
          'jobTitle': AUTHOR['job'], 'knowsAbout': AUTHOR['knows'],
          'description': f"Vystudovala obor {AUTHOR['education']}, pracuje jako {AUTHOR['job']} a píše web {SITE_NAME}.",
          'address': {'@type': 'PostalAddress', 'addressLocality': AUTHOR['locality'], 'addressCountry': AUTHOR['country']}}
WEBSITE = {'@type': 'WebSite', '@id': SITE_URL + '#website', 'url': SITE_URL, 'name': SITE_NAME,
           'description': SITE_DESC, 'inLanguage': 'cs', 'publisher': {'@id': SITE_URL + '#org'}}


def crumbs_of(path):
    meta = PAGES[path]
    trail = [(SITE_NAME, 'index.html')]
    kind = meta['kind']
    if kind in ('hub', 'branch', 'chapter'):
        trail.append(('Wetware', 'pages/wetware.html'))
    if kind == 'branch':
        trail.append((meta['name'], path))
    if kind == 'chapter':
        trail.append((PAGES[meta['branch']]['name'], meta['branch']))
    if kind in ('blog', 'post'):
        trail.append(('Blog', 'pages/blog.html'))
    if kind in ('chapter', 'post', 'stub', 'hub', 'about'):
        trail.append((meta['name'], path))
    seen, out = set(), []
    for name, p in trail:
        if p not in seen:
            seen.add(p)
            out.append((name, p))
    return out


def image_of(path):
    slug = Path(path).stem
    own = f'assets/og/{slug}.jpg'
    return own if (ROOT / own).exists() else DEFAULT_IMAGE


def graph_of(path, page_html, dates):
    meta, url = PAGES[path], url_of(path)
    kind = meta['kind']
    image = SITE_URL + image_of(path)
    nodes = [ORG, WEBSITE]
    page = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': meta['title'],
            'description': meta['desc'], 'inLanguage': 'cs', 'isPartOf': {'@id': SITE_URL + '#website'},
            'primaryImageOfPage': {'@type': 'ImageObject', 'url': image}}
    crumbs = crumbs_of(path)
    if len(crumbs) > 1:
        nodes.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': url_of(p)} for i, (n, p) in enumerate(crumbs)]})
        page['breadcrumb'] = {'@id': url + '#breadcrumb'}
    if kind in ('hub', 'branch', 'blog'):
        page['@type'] = 'CollectionPage'
        if kind == 'hub':
            chapters = [p for p, m in PAGES.items() if m['kind'] == 'chapter']
            page['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1, 'url': url_of(p), 'name': PAGES[p]['name']}
                for i, p in enumerate(chapters)]}
        if kind == 'branch':
            page['hasPart'] = [{'@id': url_of(p) + '#article'} for p, m in PAGES.items()
                               if m['kind'] == 'chapter' and m['branch'] == path]
        if kind == 'blog':
            posts = [p for p, m in PAGES.items() if m['kind'] == 'post']
            nodes.append({'@type': 'Blog', '@id': url + '#blog', 'name': f'Blog – {SITE_NAME}', 'url': url,
                          'inLanguage': 'cs', 'publisher': {'@id': SITE_URL + '#org'},
                          'blogPost': [{'@id': url_of(p) + '#article'} for p in posts]})
    if kind in ('chapter', 'post'):
        article = {'@id': url + '#article', 'headline': meta['name'], 'description': meta['desc'],
                   'inLanguage': 'cs', 'url': url, 'mainEntityOfPage': {'@id': url + '#webpage'},
                   'image': {'@type': 'ImageObject', 'url': image, 'width': 1200, 'height': 630},
                   'datePublished': meta.get('date') or dates[0], 'dateModified': dates[1],
                   'author': {'@id': PERSON_ID}, 'publisher': {'@id': SITE_URL + '#org'},
                   'isAccessibleForFree': True,
                   'about': [{'@type': 'Thing', 'name': a} for a in meta.get('about', [])],
                   'keywords': ', '.join(meta.get('about', []))}
        words = len(re.findall(r'\w+', markdown_of(path, page_html)))
        article['wordCount'] = words
        article['timeRequired'] = f'PT{max(1, round(words / WPM))}M'
        cites = sources_of(page_html)
        if cites:
            article['citation'] = cites
        if kind == 'chapter':
            article['@type'] = ['Article', 'LearningResource']
            article['learningResourceType'] = 'kapitola s interaktivními simulacemi'
            article['interactivityType'] = 'mixed'
            article['isPartOf'] = {'@type': 'CreativeWorkSeries', '@id': SITE_URL + 'pages/wetware.html#series',
                                   'name': 'Wetware', 'url': SITE_URL + 'pages/wetware.html'}
            article['articleSection'] = PAGES[meta['branch']]['name']
        else:
            article['@type'] = 'BlogPosting'
            article['isPartOf'] = {'@id': SITE_URL + 'pages/blog.html#blog'}
            article['mentions'] = [{'@type': 'Article', 'name': PAGES[p]['name'], 'url': url_of(p)}
                                   for p, m in PAGES.items() if m['kind'] == 'chapter']
        nodes.append(article)
        nodes.append(PERSON)
        faqs = faqs_of(page_html)
        if faqs:
            page['@type'] = ['WebPage', 'FAQPage']
            page['mainEntity'] = [{'@type': 'Question', 'name': q,
                                   'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]
    if kind == 'about':
        page['@type'] = 'AboutPage'
        page['mainEntity'] = {'@id': PERSON_ID}
        nodes.append(PERSON)
    nodes.insert(2, page)
    return {'@context': 'https://schema.org', '@graph': nodes}


# ------------------------------------------------------------------ head block
BEGIN, END = '<!-- seo:begin – generuje tools/seo.py, neupravovat ručně -->', '<!-- seo:end -->'


def head_block(path, page_html, dates):
    meta, url = PAGES[path], url_of(path)
    kind = meta['kind']
    image = SITE_URL + image_of(path)
    esc = lambda s: html.escape(s, quote=True)
    robots = 'index, follow, max-image-preview:large' if kind in INDEXABLE else 'noindex, follow'
    og_type = 'article' if kind in ('chapter', 'post') else ('profile' if kind == 'about' else 'website')
    lines = [BEGIN,
             f'<meta name="description" content="{esc(meta["desc"])}">',
             f'<meta name="robots" content="{robots}">']
    if kind in ('chapter', 'post', 'about'):
        lines.append(f'<meta name="author" content="{esc(AUTHOR["name"])}">')
    if kind != '404':
        lines.append(f'<link rel="canonical" href="{esc(url)}">')
    lines += [f'<meta name="theme-color" content="{THEME_COLOR}">',
              f'<meta property="og:site_name" content="{SITE_NAME}">',
              '<meta property="og:locale" content="cs_CZ">',
              f'<meta property="og:type" content="{og_type}">',
              f'<meta property="og:title" content="{esc(meta.get("name") if kind in ("chapter", "post") else meta["title"])}">',
              f'<meta property="og:description" content="{esc(meta["desc"])}">',
              f'<meta property="og:url" content="{esc(url)}">',
              f'<meta property="og:image" content="{esc(image)}">',
              '<meta property="og:image:width" content="1200">',
              '<meta property="og:image:height" content="630">',
              f'<meta property="og:image:alt" content="{esc(meta.get("name", SITE_NAME))} – {SITE_NAME}">',
              '<meta name="twitter:card" content="summary_large_image">']
    if og_type == 'profile':
        lines.append(f'<meta property="profile:first_name" content="{esc(AUTHOR["name"])}">')
    if og_type == 'article':
        lines += [f'<meta property="article:published_time" content="{meta.get("date") or dates[0]}">',
                  f'<meta property="article:modified_time" content="{dates[1]}">']
        if kind == 'chapter':
            lines.append(f'<meta property="article:section" content="{esc(PAGES[meta["branch"]]["name"])}">')
    if kind in INDEXABLE:
        data = json.dumps(graph_of(path, page_html, dates), ensure_ascii=False, indent=1).replace('</', '<\\/')
        lines.append('<script type="application/ld+json">\n' + data + '\n</script>')
    lines.append(END)
    return '\n'.join(lines)


def apply(path):
    f = ROOT / path
    s = f.read_text(encoding='utf-8')
    s = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
    s = re.sub(r'<meta name="description"[^>]*>\n?', '', s)
    dates = git_dates(path)
    title = html.escape(PAGES[path]['title'], quote=False)
    s, n = re.subn(r'<title>.*?</title>', f'<title>{title}</title>', s, count=1, flags=re.S)
    if not n:
        raise SystemExit(f'{path}: no <title>')
    i = s.index('</title>') + len('</title>')
    s = s[:i] + '\n' + head_block(path, s, dates) + s[i:]
    f.write_text(s, encoding='utf-8')
    return dates


# ------------------------------------------------------------------ site files
def write_site_files(all_dates):
    urls = []
    for path, meta in PAGES.items():
        if meta['kind'] in INDEXABLE:
            urls.append(f'  <url><loc>{html.escape(url_of(path))}</loc><lastmod>{all_dates[path][1][:10]}</lastmod></url>')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + '\n'.join(urls) + '\n</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(
        '# Větev na větvi – vyhledávače i jazykové modely jsou vítány.\n'
        'User-agent: *\nAllow: /\n\n'
        f'Sitemap: {SITE_URL}sitemap.xml\n', encoding='utf-8')

    chapters = [p for p, m in PAGES.items() if m['kind'] == 'chapter']
    posts = [p for p, m in PAGES.items() if m['kind'] == 'post']
    lines = [f'# {SITE_NAME}', '', f'> {SITE_DESC}', '', f'English summary: {SITE_DESC_EN}', '',
             'Texty jsou česky a oslovují čtenáře tykáním. Kapitoly stavějí na několika hlavních myšlenkách, přirovnáních ze '
             'života, interaktivních simulacích, odpovědích na časté otázky a zdrojích s odkazy na učebnice a články '
             '(Alberts, Boron a Boulpaep, Lehninger, Rosenbaum a další). Parametry simulací jsou u každé kapitoly '
             'popsané jako ilustrační tam, kde nejsou převzaté ze zdrojů.', '',
             '## Wetware – první kapitoly', '']
    for p in chapters:
        m = PAGES[p]
        lines.append(f'- [{m["name"]}]({url_of(p)}) ({PAGES[m["branch"]]["name"]}): {m["desc"]} English: {m["en"]}')
    lines += ['', '## Blog', '']
    for p in posts:
        m = PAGES[p]
        lines.append(f'- [{m["name"]}]({url_of(p)}): {m["desc"]} English: {m["en"]}')
    lines += ['', '## O autorce', '',
              f'- [O mně]({url_of("pages/o-mne.html")}): {AUTHOR["name"]} vystudovala obor {AUTHOR["education"]} '
              f'a pracuje jako {AUTHOR["job"]} ({AUTHOR["locality"]}). Kapitoly píše s pomocí AI (Claude od Anthropicu); '
              'fakta a čísla se ověřují proti citovaným učebnicím.']
    lines += ['', '## Rozcestníky', '',
              f'- [Rozcestník]({SITE_URL}): hlavní strana webu',
              f'- [Wetware]({url_of("pages/wetware.html")}): přehled všech větví a kapitol',
              f'- [Blog]({url_of("pages/blog.html")}): kratší texty mezi kapitolami', '',
              '## Optional', '',
              f'- [Plné texty]({SITE_URL}llms-full.txt): všechny kapitoly a články jako prostý text v Markdownu', '']
    (ROOT / 'llms.txt').write_text('\n'.join(lines), encoding='utf-8')

    full = [f'# {SITE_NAME} – plné texty', '', f'> {SITE_DESC}', '',
            'Simulace jsou nahrazené svými popisky. Zdroje jsou na konci každého textu.', '']
    for p in chapters + posts:
        m = PAGES[p]
        page_html = (ROOT / p).read_text(encoding='utf-8')
        md = markdown_of(p, page_html)
        md = re.sub(r'^# .*\n', '', md)   # the title comes from the header below
        section = PAGES[m['branch']]['name'] if m['kind'] == 'chapter' else 'Blog'
        full += ['', '---', '', f'# {m["name"]}', '', f'URL: {url_of(p)}  ', f'Větev: {section}  ',
                 f'Shrnutí: {m["desc"]}  ', f'English: {m["en"]}', '', md.strip(), '']
    (ROOT / 'llms-full.txt').write_text(re.sub(r'\n{3,}', '\n\n', '\n'.join(full)).strip() + '\n', encoding='utf-8')


def main():
    missing = sorted(set(str(p.relative_to(ROOT)) for p in list(ROOT.glob('pages/*.html')) + [ROOT / 'index.html', ROOT / '404.html'])
                     - set(PAGES))
    if missing:
        print('Pozor, tyto stránky nejsou v PAGES a zůstaly beze změny:', ', '.join(missing), file=sys.stderr)
    all_dates = {}
    for path in PAGES:
        all_dates[path] = apply(path)
    write_site_files(all_dates)
    print(f'{len(PAGES)} stránek, sitemap.xml, robots.txt, llms.txt a llms-full.txt hotové.')


if __name__ == '__main__':
    main()
