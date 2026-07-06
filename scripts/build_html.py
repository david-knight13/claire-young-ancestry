"""Build claire-young-ancestry/index.html from the Knight template + Claire's data.

Clones the (generic, data-driven) Knight fan-chart page, embeds Claire's dataset,
rebrands the Knight/America-250 copy, defaults to Country colour mode (her tree is
mostly European), and extends the US state map/gradient with the handful of extra
states present in Claire's American branch.
"""
import io, os, re

here = os.path.dirname(os.path.abspath(__file__))
proj = os.path.dirname(here)
root = os.path.dirname(proj)

tpl = io.open(os.path.join(root, 'knight-family-ancestry', 'index.html'), encoding='utf-8').read()
data = io.open(os.path.join(proj, 'data', 'fan-data-clean.json'), encoding='utf-8').read()

# 1) swap embedded dataset
tpl = re.sub(
    r'(<script id="data" type="application/json">).*?(</script>)',
    lambda m: m.group(1) + data + m.group(2),
    tpl, count=1, flags=re.S)

def rep(old, new, n=1):
    global tpl
    cnt = tpl.count(old)
    assert cnt >= 1, f'NOT FOUND: {old[:70]!r}'
    tpl = tpl.replace(old, new, n)

# 2) titles / headings
rep('<title>American Ancestry of David Knight — Fan Chart</title>',
    '<title>Ancestry of Claire Young — Fan Chart</title>')
rep('<h1>American Ancestry of David Knight</h1>',
    '<h1>Ancestry of Claire Young</h1>')

# 3) subtitle line (counts + commemoration) — precise, semicolon-safe edits
rep("DATA.meta.nodes+' ancestors in America · '",
    "(DATA.meta.unique||DATA.meta.nodes)+' documented ancestors · '")
rep("' with notable facts &nbsp;·&nbsp; '",
    "' with titles or rank &nbsp;·&nbsp; '")
tpl = re.sub(r'(<span class="commem">).*?(</span>)',
             r'\1Traced from FamilySearch · root L6J4-82H\2', tpl, count=1)

# 4) default to country mode (chart + report) since the tree is mostly European
rep("let colorMode='state';", "let colorMode='country';")
rep("let reportMode='state';", "let reportMode='country';")
rep('<button class="btn wide" id="countryToggle">◍ Country mode</button>',
    '<button class="btn wide on" id="countryToggle">◍ Country mode  ✓</button>')

# 5) trace depth: Claire's data reaches generation 14
rep('const TARGET_GEN=13;', 'const TARGET_GEN=14;')

# 6) legend note + report subtitle copy
rep('Colors run as a geographic gradient — Florida through Illinois and up to New Hampshire — so neighboring states are neighboring colors. <b>Click a state</b> here or on the map to wash out all others. Click any slice to open a person and zoom to them; the slice turns <b>white</b> while selected. Zoom in to reveal names. Faint <b>dashed grey wedges</b> mark branches whose ancestry is still undocumented.',
    'This tree is mostly European, so it opens in <b>Country mode</b> — switch with the ◍ button. In <b>State / Colony</b> mode, U.S. colours run as a geographic gradient so neighbouring states share neighbouring hues. <b>Click a country or state</b> here to wash out all others. Click any slice to open a person and zoom to them; the slice turns <b>white</b> while selected. Zoom in to reveal names. Faint <b>dashed grey wedges</b> mark branches whose ancestry is still undocumented.')
rep('The direct ancestors of David Knight, generations 1 through ${TARGET_GEN} ',
    'The direct ancestors of Claire Young, generations 1 through ${TARGET_GEN} ')

# 7) extend US state grid + gradient with states in Claire's American branch
rep("'Acadia':[12,0,'AC'],'Nova Scotia':[12,1,'NS']\n};",
    ("'Acadia':[12,0,'AC'],'Nova Scotia':[12,1,'NS'],\n"
     "  'Ohio':[8,2,'OH'],'Michigan':[8,1,'MI'],'Iowa':[5,3,'IA'],'Minnesota':[5,2,'MN'],\n"
     "  'South Dakota':[4,3,'SD'],'Kansas':[4,5,'KS'],'California':[1,4,'CA']\n};"))
rep("'Massachusetts','New Hampshire','Maine','Acadia','Nova Scotia','Oregon'];",
    ("'Massachusetts','New Hampshire','Maine','Acadia','Nova Scotia',\n"
     "  'Ohio','Michigan','Iowa','Minnesota','South Dakota','Kansas','Oregon','California'];"))

out = os.path.join(proj, 'index.html')
io.open(out, 'w', encoding='utf-8').write(tpl)
print('wrote', out, '(', len(tpl), 'bytes )')
