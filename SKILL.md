---
compatibility: Claude.ai, Claude Chat, Claude Code
metadata:
  "Built and maintained": "Darrin Southern from CadenceUX"
  version: "1.4"
name: monkeybread-mbs-plugin
description: |
  Reference skill for the MBS FileMaker Plugin by Monkeybread Software — covers all
  7,807 functions across 245 components (SQL, SyntaxColoring, GameKit, DynaPDF, XL,
  CURL, GMImage, Events, WebView, Window, FM, JSON, MapView, MongoDB, Files, Text,
  ListDialog, MenuItem, Dialog, Math, and many more), including 396 deprecated
  functions, current as of plugin version 16.3. Use whenever an
  MBS( "Component.Function"; ... ) call appears in a FileMaker calculation or script,
  or when the user asks about the MBS Plugin, Monkeybread Software, or a specific MBS
  function. Reference data lives in references/group-NN.json (20 grouped files),
  indexed by references/index.json. Every entry has a status — free, licensed (works
  unregistered, nags with a reminder dialog until registered), or unknown_license (no
  vendor marker) — plus a requires_addon note for DynaPDF/XL/Saxon, which need a
  separate paid add-on. Flag licensed, unknown, add-on, and deprecated status — don't
  assume free or current.
---

# MBS FileMaker Plugin — Reference Skill

**Vendor:** Monkeybread Software (Christian Schmitz)
**Source:** Live crawl of the vendor's documentation site `mbsplugins.eu` — enumerated
from its markdown mirror (`index.md` → `component_X.md` pages, plus `deprecated.md`),
detail parsed from the matching `.shtml` pages (only the HTML carries the paste-ready
`fmxmlsnippet` examples).
**Plugin version at build:** 16.3 was the latest *released* version (per the vendor's
release notes page) when this catalog was built/rebuilt on 2026-07-23. (The 16.2-era
build tagged 39 functions `prerelease: true` because 16.3 was still in development
then — this rebuild, after 16.3 shipped on 21 July 2026, confirmed all 39 against the
vendor's own release notes and cleared the flag; none currently carry it.)
**Live doc URL pattern:** `https://www.mbsplugins.eu/{FunctionName}.md` (strip the dots
from the function name, e.g. `Dialog.GetFieldText` → `DialogGetFieldText.md`). The `.md`
pages are clean markdown — much better for fetching than the older `.shtml` pattern,
which still works for anything the `.md` mirror lacks.
**Live release notes (for version self-check):** `https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`

This catalog covers **all 7,807 MBS functions** linked from the vendor's component and
deprecated listing pages at build time. (The site's `index.md` headline counter said
7,919 — the ~112 residual isn't linked from any listing page; the enumerated set is a
strict superset of the previous docset-based catalog and includes every function on the
newest `newinversionNNN.md` release pages.) Every entry has a `status` field:

| Status | Meaning |
|---|---|
| `free` (2,553) | Vendor doc page states the function works unregistered, no reminder dialog. |
| `licensed` (4,682) | Paid-tier function. It still runs and returns a real result on an unregistered (free-tier) install — it does **not** fail or return an error. The only consequence of being unregistered is a periodic reminder dialog (per Monkeybread's own [Free Tier announcement](https://www.mbsplugins.de/archive/2023-01-30/Free_Tier_for_MBS_FileMaker_Pl/monkeybreadsoftware_blog_filemaker), it surfaces every few minutes while any licensed function is in use) until the base MBS plugin is registered. |
| `unknown_license` (572) | Neither marker is present on the vendor's page. Genuinely unconfirmed; say so rather than guessing free or licensed. |

Two boolean flags sit alongside `status` on every entry:

- **`deprecated` (396 functions)** — listed on the vendor's deprecated-functions page
  (`https://www.mbsplugins.eu/deprecated.md`). These still exist and run, but the vendor
  recommends a replacement — check the function's own doc page for what to use instead,
  and steer users toward the replacement in new code. Whole components can be deprecated
  (Calendar and Addressbook are the largest — superseded by the newer Events and Contacts
  components).
- **`prerelease` (0 functions currently)** — documented by the vendor for a plugin version
  *newer than the latest shipped release* at build time. None right now, since this build
  is current with the latest shipped release (16.3). If the field is `true` on any entry
  in a future rebuild, it means the vendor's docs are ahead of what's released — tell the
  user the function may not be in their installed plugin yet, and treat the flag as
  stale-conservative once that version ships (the function simply works by then; the next
  rebuild clears it).

Three components additionally require a **separate paid add-on** beyond the base MBS
plugin registration — check `requires_addon` on the component file (also listed in
`references/index.json` under `addon_components`):

| Component | Add-on |
|---|---|
| DynaPDF | Starter $249 / Lite $499 / Pro $899 / Enterprise $1,599, plus an optional PDF/A add-on |
| XL | LibXL license, $219/platform or $1,199 Enterprise |
| Saxon | Saxon-PE $325/yr or Saxon-EEV $800/yr |

When answering about a `licensed` function, tell the user it works unregistered but
will trigger a periodic reminder dialog until the base plugin is licensed — don't
imply it fails outright. For `unknown_license` functions, or anything in
DynaPDF/XL/Saxon (which need their own separate paid add-on on top of base
registration), say the licensing/add-on requirement is unconfirmed or required
rather than assuming it'll just work with no consequence.

## How to look up a function

1. Open `references/index.json` — it maps each component (e.g. `Dialog`, `SQL`, `JSON`)
   to the **grouped file** it lives in under `references/` (`group-01.json` ...
   `group-20.json`), a function count, and per-status/prerelease/deprecated breakdowns.
   Components are bin-packed into 20 group files by size, not one file per component —
   there's no way to guess the right group file from the component name alone, always
   check `index.json` first.
2. The component is the part before the first `.` in the function name
   (`SQL.NewConnection` → component `SQL`). Top-level functions with no dot in the name
   (`Trace`, `IsError`, `ClearRegistration`, ...) are each their own component key equal
   to the function name. A handful of functions have a mis-cased component prefix on the
   vendor's own site (e.g. `Webview.X` instead of `WebView.X`) — this catalog normalizes
   those into the majority-casing component, so look up by the component name in
   `index.json`, not by guessing case from the function name alone.
3. Open the group file `index.json` pointed to, read its `components` object, find
   the matching component key, then find the function by exact `name` match within
   that component's `functions` array.
4. Each entry is self-contained: `signature`, `description`, structured `parameters`
   (name, description, example, `optional` flag), `result`, `version_introduced`,
   `prerelease`, `deprecated`, `compatibility` (bools for macos/windows/linux/server/
   ios_sdk), `status`, `examples` (paired `text_code` + `xml_code` — the `xml_code` is
   a ready-to-paste `fmxmlsnippet` for a `Set Variable` step calling the function),
   `see_also`, and `url` (the function's live `.md` doc page, for cross-checking or if
   the catalog looks stale).

No need to fetch the `url` for routine lookups — it's only useful to verify against
the live page or check for updates since this catalog was built.

---

## MBS Plugin version self-check

This watches the **vendor's** plugin for new releases (distinct from the *Skill update self-check*
below, which watches this skill's own repo). At the start of each session — on the first
MBS-related question — run this check once:

1. `web_fetch` `https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`
2. Find the topmost "Release notes for version X.X" heading — this is the current
   plugin version Monkeybread Software has released.
3. Compare it with this catalog's `plugin_version_released_at_build` (currently `"16.3"`
   — see `references/index.json`).
4. If the live version is higher, prepend this notice to your first response:

   > ⚠️ **MBS Plugin update available**
   > A newer MBS plugin version is out (v[X.X]). This skill's catalog was built when
   > v16.3 was the latest release. Functions added after the build won't be here —
   > check `https://www.mbsplugins.eu/{FunctionName}.md` for anything not found
   > locally, or regenerate the catalog (see "Regenerating the catalog" below). If any
   > entries in this catalog are tagged `prerelease: true` for the new version, treat
   > them as current now that it's shipped, and rebuild when convenient to clear the
   > flags.

5. Do not repeat the notice again in the same session.
6. If the fetch fails, times out, or the page layout has changed, skip silently —
   do not surface the error or block the user's actual question.

A cheaper secondary signal, useful when asked "is this catalog current?": fetch
`https://www.mbsplugins.eu/index.md` (one small page) and compare its "Currently N
functions" headline against `site_function_count_at_build` (7,919) in
`references/index.json` — if the live number is higher, the vendor has documented new
functions since this build. And `https://www.mbsplugins.eu/newinversion{NNN}.md` (e.g.
`newinversion164.md`) lists exactly which functions a given version added — the fastest
way to see what a rebuild would pick up.

This check is advisory only — never refuse to answer a function lookup because the
plugin version check failed or because a newer version exists.

---

## Skill update self-check

Distinct from the MBS Plugin version check above (which watches the vendor) — this checks whether
a newer release of **this skill** exists. At the start of each session, on the first MBS-related
question, run once:

1. Fetch `https://github.com/CadenceUX/monkeybread-mbs-plugin-skill/raw/main/VERSION`
2. Parse the returned string as the latest available version
3. Compare with this skill's installed version (currently `"1.4"`)
4. If latest > installed, prepend this notice to your first response:

   > ⚠️ **Skill update available**
   > This skill is v[installed]. v[latest] is available at
   > https://github.com/CadenceUX/monkeybread-mbs-plugin-skill/releases
   > Update your local skill files to get the latest MBS coverage.

5. Do not repeat the notice again in the same session.
6. If the fetch fails or returns an unexpected value, skip silently — do not surface the error.

---

## Version drift detection (per live lookup)

When fetching a specific function's live `.md` page (`url` field) to verify or supplement
a catalog entry, the page's own platform table shows the version that introduced it.
If that version is higher than `16.3` and the function isn't already tagged `prerelease`
in this catalog, the function was added after this catalog was built — note that to the
user rather than treating the live page's extra detail as already reflected locally.

## Documentation freshness check (per live lookup)

Distinct from the version-introduced check above and from the plugin-release check further up —
this is about whether a function's *doc page text itself* has been edited since the catalog was
built, independent of either the plugin version or when the function was introduced. Monkeybread's
doc pages carry a "Created [date], last changed [date]" line near the bottom of the page (present
in both the `.md` and `.shtml` versions):

1. When fetching a function's live page to verify or supplement a catalog entry, look for the
   "last changed" date in the page text.
2. This catalog doesn't store that date per function, so there's no exact baseline to diff
   against — treat it as **informational context** for the user (e.g. "this page was last edited
   on [date]") rather than a firm drift flag.
3. If the "last changed" date is after 2026-07-23 (this catalog's build date) and the user's
   question concerns exact parameter behaviour or option names, mention that the live page may
   have details not reflected in the local catalog.
4. Skip this for routine lookups — only worth doing when the user asks if something is current, or
   when local catalog details seem to disagree with observed plugin behaviour.

## Component quick index (top 20 by total function count)

| Component | Total | Free | Licensed | Unknown | Group file |
|---|---|---|---|---|---|
| DynaPDF | 651 | 17 | 624 | 10 | references/group-01.json |
| XL | 470 | 3 | 364 | 103 | references/group-03.json |
| CURL | 459 | 62 | 141 | 256 | references/group-02.json |
| GMImage | 366 | 8 | 350 | 8 | references/group-04.json |
| Events | 178 | 12 | 166 | 0 | references/group-10.json |
| WebView | 158 | 10 | 130 | 18 | references/group-08.json |
| SQL | 143 | 128 | 9 | 6 | references/group-07.json |
| SyntaxColoring | 129 | 129 | 0 | 0 | references/group-15.json |
| Window | 127 | 26 | 101 | 0 | references/group-16.json |
| FM | 119 | 52 | 67 | 0 | references/group-05.json |
| MongoDB | 110 | 14 | 93 | 3 | references/group-11.json |
| JSON | 108 | 38 | 66 | 4 | references/group-09.json |
| MapView | 99 | 62 | 14 | 23 | references/group-16.json |
| Calendar (deprecated) | 99 | 0 | 99 | 0 | references/group-20.json |
| GameKit | 97 | 97 | 0 | 0 | references/group-13.json |
| Files | 92 | 17 | 73 | 2 | references/group-12.json |
| Text | 87 | 27 | 59 | 1 | references/group-13.json |
| SystemInfo | 87 | 86 | 1 | 0 | references/group-17.json |
| Addressbook (deprecated) | 85 | 36 | 49 | 0 | references/group-14.json |
| MenuItem | 76 | 36 | 40 | 0 | references/group-19.json |

245 components are packed into 20 group files total — see `references/index.json`
for the full component → group-file mapping and per-component breakdowns.
Group-file numbers shift on every rebuild (bin-packing is size-based, not stable
per component), so always resolve via `index.json` rather than hardcoding a path.

## Notes on the data

- All MBS calls use the form `MBS( "Component.Function"; Param1 ; Param2 ; ... )` —
  optional trailing parameters are wrapped in `{ }` in the signature line. Top-level
  functions take the form `MBS( "FunctionName" )` with no component prefix.
- `compatibility` reflects the vendor's own per-platform support table — check it before
  suggesting a function for a Server-side script or iOS SDK app; many functions
  (e.g. most `Dialog.*`) are macOS/Windows-only and return an error on Server or iOS.
- `examples[].xml_code`, when present (4,015 functions have at least one), is a verbatim
  `fmxmlsnippet` block from the vendor's doc page (a `Set Variable [ $r ; ... ]` step
  calling the function) — usable directly with this project's `/api/hr-to-xml` /
  `/api/xml-to-hr` round-trip workflow if editing a script that needs this call inserted.
- `status: "unknown_license"` is not the same as `"free"` — 572 functions across 38
  components (mostly CURL, XL, Overlay, MapView, WebView, Llama) have no licensing
  marker on the vendor's own doc page. Don't tell a user a function is free just
  because it's in this catalog — check `status` first.
- Deprecated functions were **absent** from catalog versions before v1.3 (the vendor's
  docset didn't index most of them) — their presence here is deliberate, so Claude can
  explain legacy scripts and point at replacements, not an endorsement for new code.

## Regenerating the catalog

**This requires Claude Code (or the Agent SDK) — it does not work in plain Claude.ai chat.**
`scripts/build_catalog.py` needs a real Python interpreter with the third-party `bs4`
(BeautifulSoup) package, network access to `mbsplugins.eu`, and writes actual files on disk.
Claude.ai chat with no code execution can only read this script's text, not run it. Run this
from Claude Code, or by hand in a local Python environment.

No vendor download is needed any more (the old docset pipeline is retired) — the script
crawls the live documentation site directly:

```
python3 scripts/build_catalog.py references/ /path/to/fetch-cache
```

The optional second argument is a cache directory so an interrupted or repeated run doesn't
refetch all ~8,000 pages (a full cold crawl takes roughly 10–20 minutes at the script's
polite 8-way concurrency). **Delete the cache (or point at a fresh directory) when
rebuilding for a new plugin version** — cached pages are never revalidated. The script
re-derives everything per run: latest released version from the release notes page,
function enumeration from the component + deprecated pages, and per-function
status/prerelease/deprecated flags. It fails loudly (exit 1, listing the pages) if any
function page can't be fetched, rather than shipping silent gaps.

Re-run it after a plugin release to pick up new functions and clear stale `prerelease`
flags. Group-file assignments are recomputed from scratch each run — don't rely on a
component staying in the same `group-NN.json` across rebuilds.

---

## Licence

This skill is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
