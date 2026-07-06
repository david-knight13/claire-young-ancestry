# Claire Young Ancestry — Interactive Fan Chart

An interactive, zoomable fan chart of the ancestry of **Claire Young**
(FamilySearch person `L6J4-82H`), traced from FamilySearch.

Open `index.html` in any browser — the dataset is embedded, so no server is needed.

## What it shows

- **1,320 documented ancestors** (1,453 chart positions, including pedigree
  collapse) traced across **15 generations** (the subject plus 14 ascending).
- **Fan Chart tab** — a colour-coded radial pedigree:
  - Opens in **Country mode**, because this tree is mostly European (England,
    Belgium, Germany, Switzerland, Ireland, the Netherlands, France, Scotland …).
  - Switch to **State / Colony mode** for the American branch (Virginia, Maryland,
    New York and other colonial mid-Atlantic lines), coloured as a geographic
    gradient so neighbouring states share neighbouring hues.
  - **Generation-depth slider** to control how many rings are shown.
  - Click any ancestor to open a detail panel with vitals and a link to their
    FamilySearch profile; from there you can re-centre the chart on that person.
  - Dashed grey wedges mark branches whose ancestry is still undocumented.
- **Summary Report tab** — cumulative pie charts of ancestral origins per
  generation, toggleable between countries and U.S. states/colonies.
- **Titled & Ranked Ancestors** sidebar — ancestors whose recorded names carry a
  genuine title or rank prefix (Sir/Dame, Col/Capt/Lt, Rev, Hon, or a
  "<Title> of <place>" nobility form), split into American/colonial and
  European/other tabs. This is derived strictly from the name field — no
  biographies are invented.

## Repository layout

```
index.html                  Self-contained interactive chart (data embedded)
data/fan-data-clean.json    The built dataset embedded into the page
data/skeleton-crawl.json    Raw ancestry skeleton (ids, names, lifespans, parent links)
data/vitals-cards.json      Raw per-person vitals (birth/death dates + places)
scripts/build_data.py       Transforms the raw crawl into fan-data-clean.json
scripts/build_html.py       Embeds the dataset into the page (built from the
                            generic Knight fan-chart template)
```

## Rebuilding

```
python scripts/build_data.py    # data/*.json  -> data/fan-data-clean.json
python scripts/build_html.py    # template + dataset -> index.html
```

`build_html.py` reuses the data-driven page template from the sibling
`knight-family-ancestry` project, rebranded for Claire and defaulted to
Country colour mode.

## How the data was gathered

Crawled through an authenticated FamilySearch session using the site's internal
tree-data service:

1. **Skeleton** — breadth-first over `r9/portrait-pedigree` (8 generations per
   call, re-rooting at the frontier) to collect every ancestor's id, name,
   lifespan and parent links, bounded at generation 14 so all branches are
   traced equally far.
2. **Vitals** — `v8/person/{id}/card` for each ancestor, for birth/death dates
   and places.

## Data source

Genealogical data is drawn from [FamilySearch](https://www.familysearch.org/).
Living individuals carry no places (private); about 82% of ancestors have a
recorded birthplace.
