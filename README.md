# monkeybread-mbs-plugin

A Claude.ai skill providing reference data for the **MBS FileMaker Plugin** by
Monkeybread Software (Christian Schmitz) — function signatures, parameters,
platform compatibility, and examples for FileMaker scripting and calculations
that call `MBS( "Component.Function"; ... )`.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).

## Scope

Built 2026-07-05 from a live crawl of the vendor's documentation site
(`mbsplugins.eu`), when **16.2** was the latest released plugin version. Covers
**all 7,807 functions** across 245 components (SQL, JSON, Dialog, FM, CURL,
DynaPDF, XL, GMImage, Events, WebView, Math, Text, SystemInfo, and many more —
see `SKILL.md` for the top-20 table and `references/index.json` for the full
list). Every function is tagged with a `status`:

| Status | Count | Meaning |
|---|---|---|
| `free` | 2,553 | Works unregistered, per the vendor's doc page, no reminder dialog |
| `licensed` | 4,682 | Paid-tier function — still runs and returns a real result unregistered, but nags with a periodic reminder dialog until the base MBS plugin is registered |
| `unknown_license` | 572 | Vendor doc page has no marker either way — genuinely unconfirmed |

Two boolean flags sit alongside `status`:

| Flag | Count | Meaning |
|---|---|---|
| `prerelease` | 39 | Documented by the vendor for in-development plugin version 16.3, which wasn't released at build time — may not be in your installed plugin yet |
| `deprecated` | 396 | On the vendor's deprecated-functions list — still works, but a replacement is recommended |

Three components additionally need a separate paid add-on beyond the base plugin
registration — DynaPDF, XL, and Saxon — flagged via `requires_addon` on each
component's entry.

## Installing

**macOS (Claude desktop app):** double-click the `monkeybread-mbs-plugin-v1.3.skill`
file — it opens Claude's skill-install flow directly. (The `.skill` file is just the
release zip renamed.)

**Claude.ai in a browser (or if double-click doesn't work):** upload the release zip
via Settings → Customize → Skills.

## Contents

```
monkeybread-mbs-plugin/
├── SKILL.md                  Triggering description + lookup instructions
├── VERSION                   Bare version string, for the GitHub skill update self-check
├── CHANGELOG.md              Version history
├── README.md                 This file
├── references/
│   ├── index.json            Component → group-file → counts manifest
│   └── group-NN.json         20 files, components bin-packed by size
└── scripts/
    └── build_catalog.py      Regenerates references/ by crawling mbsplugins.eu
```

245 components are packed into 20 group files (not one file per component) to stay
well under the ~200-file practical ceiling on Claude.ai skill zip uploads — see
`CHANGELOG.md` v1.2. Always resolve a component's file via `references/index.json`;
group-file numbers are reassigned on every rebuild.

## Staying current

This skill checks the vendor's live release notes page once per session
(`https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`) and flags
if a newer MBS plugin version than 16.2 has been released — see "MBS Plugin
version self-check" in `SKILL.md`, which also documents a one-fetch drift signal
(the "Currently N functions" counter on `mbsplugins.eu/index.md`). Separately, a
"Skill update self-check" compares this skill's own `VERSION` against its GitHub
repo to flag when a newer release of the skill itself is available. The underlying
function data is only updated by re-running `scripts/build_catalog.py`.

## How Claude uses this skill

When a FileMaker calculation or script contains an `MBS("Component.Function"; ...)`
call, or the user asks about the MBS Plugin / Monkeybread Software / a specific
MBS function, Claude looks up the component in `references/index.json` to find
which `group-NN.json` file it lives in, opens that file, and finds the function by
exact name match within the matching component's entry. Each entry carries
everything needed to use the function correctly, including per-platform support
(macOS/Windows/Linux/Server/iOS SDK), licensing status, deprecated/prerelease
flags, and a ready-to-paste `fmxmlsnippet` example where the vendor's doc page
provides one.

## Updating the catalog

No vendor docset download is needed any more — the build script crawls the live
documentation site directly (requires Python 3 with `bs4` and network access):

```
python3 scripts/build_catalog.py references/ /path/to/fetch-cache
```

This rebuilds every file in `references/` from scratch (the optional cache
directory avoids refetching ~8,000 pages on interrupted or repeated runs — use a
fresh one when rebuilding for a new plugin version). Bump the version in
`SKILL.md` frontmatter, the `VERSION` file, and add a `CHANGELOG.md` entry before
re-packaging.

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, adapt, and redistribute with attribution.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
