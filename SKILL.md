---
compatibility: Claude.ai, Claude Chat, Claude Code
metadata:
  "Built and maintained": "Darrin Southern from CadenceUX"
  version: "1.2"
name: monkeybread-mbs-plugin
description: |
  Reference skill for the MBS FileMaker Plugin by Monkeybread Software — covers all
  7,370 functions across 233 components (SQL, SyntaxColoring, GameKit, DynaPDF, XL,
  CURL, GMImage, Events, WebView, Window, FM, JSON, MapView, MongoDB, Files, Text,
  ListDialog, MenuItem, Twain, Dialog, Math, and many more). Use whenever an
  MBS( "Component.Function"; ... ) call appears in a FileMaker calculation or script,
  or when the user asks about the MBS Plugin, Monkeybread Software, or a specific MBS
  function. Reference data lives in references/group-NN.json (20 grouped files),
  indexed by references/index.json. Every entry has a status — free, licensed (works
  unregistered, nags with a reminder dialog until registered), or unknown_license
  (vendor doc page has no marker either way) — plus a requires_addon note for
  DynaPDF/XL/Saxon, which need a separate paid add-on. Flag licensed/unknown/add-on
  status, don't assume free. Do
  not use for BaseElements/Goya (BE_ functions — see goya-be-plugin).
---

# MBS FileMaker Plugin — Reference Skill

**Vendor:** Monkeybread Software (Christian Schmitz)
**Source:** Dash docset shipped by the vendor (`MBS.docset`), parsed into structured JSON
**MBS Plugin version covered:** 16.2 — this catalog reflects the docset as of plugin
version 16.2. If a user is on a newer plugin version, functions added after 16.2 won't
be in this catalog; check the live URL pattern below or regenerate from a newer docset.
**Live fallback URL pattern:** `https://www.mbsplugins.eu/{FunctionName}.shtml` (strip the dot from the function name, e.g. `Dialog.GetFieldText` → `DialogGetFieldText.shtml`)
**Live release notes (for version self-check):** `https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`

This catalog covers **all 7,370 MBS functions**. Every entry has a `status` field:

| Status | Meaning |
|---|---|
| `free` (2,408) | Vendor doc page states the function works unregistered, no reminder dialog. |
| `licensed` (4,406) | Paid-tier function. It still runs and returns a real result on an unregistered (free-tier) install — it does **not** fail or return an error. The only consequence of being unregistered is a periodic reminder dialog (per Monkeybread's own [Free Tier announcement](https://www.mbsplugins.de/archive/2023-01-30/Free_Tier_for_MBS_FileMaker_Pl/monkeybreadsoftware_blog_filemaker), it surfaces every few minutes while any licensed function is in use) until the base MBS plugin is registered. |
| `unknown_license` (556) | Neither marker is present on the vendor's page — confirmed on the live site too, not a stale-docset artifact. Genuinely unconfirmed; say so rather than guessing free or licensed. |

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
   `group-20.json`), a function count, and a per-status breakdown. Components are
   bin-packed into 20 group files by size, not one file per component — there's no
   way to guess the right group file from the component name alone, always check
   `index.json` first.
2. The component is the part before the first `.` in the function name
   (`SQL.NewConnection` → component `SQL`). A handful of functions have a mis-cased
   component prefix on the vendor's own site (e.g. `Webview.X` instead of
   `WebView.X`) — this catalog normalizes those into the majority-casing component,
   so look up by the component name in `index.json`, not by guessing case from the
   function name alone.
3. Open the group file `index.json` pointed to, read its `components` object, find
   the matching component key, then find the function by exact `name` match within
   that component's `functions` array.
4. Each entry is self-contained: `signature`, `description`, structured `parameters`
   (name, description, example, `optional` flag), `result`, `version_introduced`,
   `compatibility` (bools for macos/windows/linux/server/ios_sdk), `status`,
   `examples` (paired `text_code` + `xml_code` — the `xml_code` is a ready-to-paste
   `fmxmlsnippet` for a `Set Variable` step calling the function), `see_also`, and
   `url` (live page, for cross-checking or if the catalog looks stale).

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
3. Compare it with this catalog's `plugin_version_covered` (currently `"16.2"` — see
   `references/index.json`).
4. If the live version is higher, prepend this notice to your first response:

   > ⚠️ **MBS Plugin update available**
   > A newer MBS plugin version is out (v[X.X]). This skill's catalog covers
   > functions up to v16.2 — new functions added since then won't be here yet.
   > Check `https://www.mbsplugins.eu/{FunctionName}.shtml` for anything not found
   > locally, or regenerate the catalog from an updated `MBS.docset` (see
   > "Regenerating the catalog" below).

5. Do not repeat the notice again in the same session.
6. If the fetch fails, times out, or the page layout has changed, skip silently —
   do not surface the error or block the user's actual question.

This check is advisory only — never refuse to answer a function lookup because the
plugin version check failed or because a newer version exists.

---

## Skill update self-check

Distinct from the MBS Plugin version check above (which watches the vendor) — this checks whether
a newer release of **this skill** exists. At the start of each session, on the first MBS-related
question, run once:

1. Fetch `https://github.com/CadenceUX/monkeybread-mbs-plugin-skill/raw/main/VERSION`
2. Parse the returned string as the latest available version
3. Compare with this skill's installed version (currently `"1.2"`)
4. If latest > installed, prepend this notice to your first response:

   > ⚠️ **Skill update available**
   > This skill is v[installed]. v[latest] is available at
   > https://github.com/CadenceUX/monkeybread-mbs-plugin-skill/releases
   > Update your local skill files to get the latest MBS coverage.

5. Do not repeat the notice again in the same session.
6. If the fetch fails or returns an unexpected value, skip silently — do not surface the error.

---

## Version drift detection (per live lookup)

When fetching a specific function's live page (`url` field) to verify or supplement a
catalog entry, the page's own platform table shows the version that introduced it.
If that version is higher than `16.2`, the function was added after this catalog was
built — note that to the user rather than treating the live page's extra detail as
already reflected locally.

## Documentation freshness check (per live lookup)

Distinct from the version-introduced check above and from the plugin-release check further up —
this is about whether a function's *doc page text itself* has been edited since the catalog was
built, independent of either the plugin version or when the function was introduced. Monkeybread's
doc pages carry a "Created [date], last changed [date]" line in the page body (visible in the raw
HTML this catalog was originally scraped from):

1. When fetching a function's live page to verify or supplement a catalog entry, look for the
   "last changed" date in the page text.
2. This catalog doesn't store that date per function, so there's no exact baseline to diff
   against — treat it as **informational context** for the user (e.g. "this page was last edited
   on [date]") rather than a firm drift flag.
3. If the "last changed" date is recent and the user's question concerns exact parameter
   behaviour or option names, mention that the live page may have details not reflected in the
   local catalog, which was built from a point-in-time snapshot.
4. Skip this for routine lookups — only worth doing when the user asks if something is current, or
   when local catalog details seem to disagree with observed plugin behaviour.

## Component quick index (top 20 by total function count)

| Component | Total | Free | Licensed | Unknown | Group file |
|---|---|---|---|---|---|
| DynaPDF | 647 | 17 | 620 | 10 | references/group-01.json |
| XL | 463 | 3 | 358 | 102 | references/group-03.json |
| CURL | 443 | 61 | 137 | 245 | references/group-02.json |
| GMImage | 365 | 8 | 349 | 8 | references/group-04.json |
| Events | 177 | 12 | 165 | 0 | references/group-10.json |
| WebView | 152 | 10 | 124 | 18 | references/group-08.json |
| SQL | 143 | 128 | 9 | 6 | references/group-07.json |
| SyntaxColoring | 122 | 122 | 0 | 0 | references/group-14.json |
| Window | 116 | 22 | 94 | 0 | references/group-16.json |
| FM | 109 | 48 | 61 | 0 | references/group-06.json |
| JSON | 108 | 38 | 66 | 4 | references/group-09.json |
| GameKit | 97 | 97 | 0 | 0 | references/group-16.json |
| MapView | 97 | 60 | 14 | 23 | references/group-19.json |
| MongoDB | 95 | 13 | 79 | 3 | references/group-13.json |
| Files | 92 | 17 | 73 | 2 | references/group-11.json |
| Text | 87 | 27 | 59 | 1 | references/group-12.json |
| Socket | 76 | 25 | 51 | 0 | references/group-18.json |
| ListDialog | 75 | 72 | 3 | 0 | references/group-09.json |
| MenuItem | 74 | 34 | 40 | 0 | references/group-17.json |
| Twain | 73 | 50 | 23 | 0 | references/group-15.json |

233 components are packed into 20 group files total — see `references/index.json`
for the full component → group-file mapping and per-component status breakdowns.
Group-file numbers shift on every rebuild (bin-packing is size-based, not stable
per component), so always resolve via `index.json` rather than hardcoding a path.

## Notes on the data

- All MBS calls use the form `MBS( "Component.Function"; Param1 ; Param2 ; ... )` —
  optional trailing parameters are wrapped in `{ }` in the signature line.
- `compatibility` reflects the vendor's own per-platform support table — check it before
  suggesting a function for a Server-side script or iOS SDK app; many functions
  (e.g. most `Dialog.*`) are macOS/Windows-only and return an error on Server or iOS.
- `examples[].xml_code`, when present, is a verbatim `fmxmlsnippet` block from the vendor's
  doc page (a `Set Variable [ $r ; ... ]` step calling the function) — usable directly
  with this project's `/api/hr-to-xml` / `/api/xml-to-hr` round-trip workflow if editing
  a script that needs this call inserted.
- `status: "unknown_license"` is not the same as `"free"` — 556 functions across 37
  components (mostly CURL, XL, Overlay, MapView, WebView) have no licensing marker on
  the vendor's own doc page, live site included. Don't tell a user a function is free
  just because it's in this catalog — check `status` first.

## Regenerating the catalog

**This requires Claude Code (or the Agent SDK) — it does not work in plain Claude.ai chat.**
`scripts/build_catalog.py` needs a real Python interpreter with `sqlite3` and the third-party
`bs4` (BeautifulSoup) package, and reads/writes actual files on disk (the `MBS.docset` bundle's
internal SQLite index plus hundreds of HTML pages, then the skill's own `references/` folder).
Claude.ai chat with no code execution can only read this script's text, not run it. Even
Claude.ai's sandboxed code-execution/Analysis tool is a poor fit — that sandbox has no access to
your local `MBS.docset` file (you'd have to upload the whole bundle into the chat) and may not
have `bs4` preinstalled. Run this from Claude Code, or by hand in a local Python environment.

**Getting the `MBS.docset` file:** download it from
`https://www.monkeybreadsoftware.com/filemaker/Dash/MBS.zip` and unzip it — that's the Dash
docset the vendor ships, and the source this catalog is built from.

`scripts/build_catalog.py` rebuilds this entire `references/` folder from a local
`MBS.docset` (the vendor ships an updated docset with new plugin versions):

```
python3 scripts/build_catalog.py /path/to/MBS.docset references/
```

Re-run this after a plugin update to pick up new or changed functions. The script
bin-packs components into `NUM_GROUPS` (currently 20) group files by serialized
size — group-file assignments are recomputed from scratch each run, so don't rely
on a component staying in the same `group-NN.json` across rebuilds.

---

## Licence

This skill is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
