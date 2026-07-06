"""Build claire-young-ancestry/data/fan-data-clean.json from the FamilySearch crawl.

Inputs (in data/):
  data/skeleton-crawl.json  - {info:{id:{name,life,gender,living}}, par:{id:[fatherId,motherId]}}
  data/vitals-cards.json    - {id:{name,gender,life,bd,bp,dd,dp}}
Output:
  data/fan-data-clean.json  - {meta, nodes:[...]} in the Knight fan-chart schema
"""
import json, io, re, os
from collections import deque, Counter

ROOT = 'L6J4-82H'
CAP = 14

here = os.path.dirname(os.path.abspath(__file__))
proj = os.path.dirname(here)
root = os.path.dirname(proj)

def load(p):
    return json.loads(io.open(p, encoding='utf-8').read())

skel = load(os.path.join(proj, 'data', 'skeleton-crawl.json'))
cards = load(os.path.join(proj, 'data', 'vitals-cards.json'))
info, par = skel['info'], skel['par']

# US state extraction (full list, gradient/grid handled in the HTML)
US_STATES = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
 'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky',
 'Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri',
 'Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina',
 'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina',
 'South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',
 'Wisconsin','Wyoming']
USSET = set(US_STATES)

def states_of(place):
    out = []
    if not place:
        return out
    for seg in [s.strip() for s in place.split(',')]:
        if seg in USSET and seg not in out:
            out.append(seg)
    return out

def year(s):
    if not s:
        return None
    m = re.search(r'(\d{4})', s)
    return m.group(1) if m else None

def life_of(c, sk):
    """Return 'YYYY-YYYY' / 'YYYY-Living' style string."""
    by = year(c.get('bd')) if c else None
    dy = year(c.get('dd')) if c else None
    living = sk.get('living') if sk else False
    if not by and not dy:
        # fall back to skeleton lifespan text ("1936-2010" / "Living")
        return (sk or {}).get('life') or ('Living' if living else 'Unknown')
    right = 'Living' if (living and not dy) else (dy or '?')
    return f"{by or '?'}–{right}"

# notability: conservative & transparent — only real titles/rank, never bare words
# (avoids flagging given names/surnames like "Prince", "King", "Earl", "Major").
# Nobility requires the "<Title> of/de/von ..." territorial pattern; rank/honour
# requires a recognised genealogical name prefix.
NOBLE_OF = re.compile(
    r'\b(King|Queen|Emperor|Empress|Prince|Princess|Archduke|Archduchess|Duke|Duchess|'
    r'Earl|Count|Countess|Margrave|Landgrave|Marquis|Marquess|Viscount|Baron|Baroness|'
    r'Lord|Lady|Duc|Duchesse|Comte|Comtesse|Graf|Gräfin|König|Herzog|Fürst)\s+'
    r'(of|de|di|von|van|du|der|the)\b', re.I)
ROYAL = re.compile(r'\b(King|Queen|Emperor|Empress|Prince|Princess|Archduke|Archduchess|König|Roi)\s+(of|de|di|von|the)\b', re.I)
KNIGHT = re.compile(r'^(Sir|Dame|Chevalier|Ritter)\s', re.I)
MILITARY = re.compile(r'^(Capt|Captain|Col|Colonel|Gen|General|Maj|Major|Lt|Lieutenant|Sgt|Sergeant|Adm|Admiral|Cpl|Ens|Ensign|Sir Knight)\.?\s', re.I)
CLERGY = re.compile(r'^(Rev|Reverend|Bishop|Deacon|Father|Pastor|Elder)\.?\s', re.I)
OFFICE = re.compile(r'^(Gov|Governor|Pres|President|Hon|Honorable|Honourable|Judge|Dr|Capt\.?|Mayor)\.?\s', re.I)

def notability(name):
    if ROYAL.search(name):
        return 6, ['Royalty']
    if NOBLE_OF.search(name):
        return 5, ['Nobility']
    if KNIGHT.match(name):
        return 4, ['Knight / Honour']
    if MILITARY.match(name):
        return 3, ['Military']
    if CLERGY.match(name):
        return 3, ['Clergy']
    if OFFICE.match(name):
        return 3, ['Office']
    return 0, []

# BFS positions (pedigree collapse allowed: every slot is its own node)
nodes = []
seenpos = set()
q = deque([(ROOT, 0, 0)])
while q:
    pid, g, p = q.popleft()
    if (g, p) in seenpos:
        continue
    seenpos.add((g, p))
    sk = info.get(pid)
    if sk is None:
        continue
    c = cards.get(pid, {})
    name = (c.get('name') or sk.get('name') or 'Unknown').strip()
    bp = c.get('bp') or ''
    dp = c.get('dp') or ''
    st = states_of(bp)
    for s in states_of(dp):
        if s not in st:
            st.append(s)
    primary = st[0] if st else 'Unknown'
    score, tags = notability(name)
    nodes.append({
        'pos': p, 'gen': g, 'id': pid, 'name': name,
        'life': life_of(c, sk), 'bp': bp, 'dp': dp,
        'states': st, 'primary': primary,
        'score': score, 'interesting': score >= 3,
        'ev': [], 'sketch': ('; '.join(tags) if tags else ''),
        'mem': 0, 'src': 0, 'story': ''
    })
    if pid in par and g < CAP:
        f, m = par[pid]
        if f and f in info:
            q.append((f, g + 1, 2 * p))
        if m and m in info:
            q.append((m, g + 1, 2 * p + 1))

maxgen = max(n['gen'] for n in nodes)
uniq = len(set(n['id'] for n in nodes))
interesting = sum(1 for n in nodes if n['interesting'])
meta = {'nodes': len(nodes), 'unique': uniq, 'maxGen': maxgen,
        'interesting': interesting, 'root': ROOT, 'rootName': 'Claire Young'}
out = {'meta': meta, 'nodes': nodes}
op = os.path.join(proj, 'data', 'fan-data-clean.json')
json.dump(out, io.open(op, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('wrote', op)
print('meta', meta)
# quick distribution
gc = Counter(n['gen'] for n in nodes)
for g in range(maxgen + 1):
    print(f'  gen {g:2d}: {gc[g]}')
