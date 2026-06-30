# monkeybread-mbs-plugin

A Claude.ai skill providing reference data for the **MBS FileMaker Plugin** by
Monkeybread Software (Christian Schmitz) — function signatures, parameters,
platform compatibility, and examples for FileMaker scripting and calculations
that call `MBS( "Component.Function"; ... )`.

Built and maintained by [Cadence UX](https://cadenceux.com.au).

## Scope

Reflects **MBS Plugin version 16.2**. Covers **all 7,370 functions** across 233
components (SQL, JSON, Dialog, FM, CURL, DynaPDF, XL, GMImage, Events, WebView,
Math, Text, SystemInfo, and many more — see `SKILL.md` for the top-20 table and
`references/index.json` for the full list). Every function is tagged with a
`status`:

| Status | Count | Meaning |
|---|---|---|
| `free` | 2,408 | Works unregistered, per the vendor's doc page, no reminder dialog |
| `licensed` | 4,406 | Paid-tier function — still runs and returns a real result unregistered, but nags with a periodic reminder dialog until the base MBS plugin is registered |
| `unknown_license` | 556 | Vendor doc page has no marker either way — genuinely unconfirmed |

Three components additionally need a separate paid add-on beyond the base plugin
registration — DynaPDF, XL, and Saxon — flagged via `requires_addon` on each
component's entry. See `CHANGELOG.md` v1.2 for how this was determined.

## Installing

Drop the `monkeybread-mbs-plugin/` folder into your Claude.ai skills directory
and restart Claude, or upload the release zip directly if your Claude.ai setup
supports skill upload.

## Contents

```
monkeybread-mbs-plugin/
├── SKILL.md                  Triggering description + lookup instructions
├── VERSION                   Bare version string, for the GitHub skill update self-check
├── CHANGELOG.md              Version history
├── README.md                 This file
├── references/
│   ├── index.json            Component → group-file → status-count manifest
│   └── group-NN.json         20 files, components bin-packed by size
└── scripts/
    └── build_catalog.py      Regenerates references/ from a local MBS.docset
```

233 components are packed into 20 group files (not one file per component) to stay
well under the ~200-file practical ceiling on Claude.ai skill zip uploads — see
`CHANGELOG.md` v1.2. Always resolve a component's file via `references/index.json`;
group-file numbers are reassigned on every rebuild.

## Staying current

This skill checks the vendor's live release notes page once per session
(`https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`) and flags
if a newer MBS plugin version than 16.2 has been released — see "MBS Plugin
version self-check" in `SKILL.md`. Separately, a "Skill update self-check"
compares this skill's own `VERSION` against its GitHub repo to flag when a newer
release of the skill itself is available. The underlying function data is only
updated by re-running `scripts/build_catalog.py` against a newer `MBS.docset`.

## How Claude uses this skill

When a FileMaker calculation or script contains an `MBS("Component.Function"; ...)`
call, or the user asks about the MBS Plugin / Monkeybread Software / a specific
MBS function, Claude looks up the component in `references/index.json` to find
which `group-NN.json` file it lives in, opens that file, and finds the function by
exact name match within the matching component's entry. Each entry carries
everything needed to use the function correctly, including per-platform support
(macOS/Windows/Linux/Server/iOS SDK) and a ready-to-paste `fmxmlsnippet` example
where the vendor's doc page provides one.

## Updating the catalog

If Monkeybread Software ships a new plugin version with an updated docset:

```
python3 scripts/build_catalog.py /path/to/new/MBS.docset references/
```

This rebuilds every file in `references/` from scratch. Bump the version in
`SKILL.md` frontmatter, the `VERSION` file, and add a `CHANGELOG.md` entry before
re-packaging.

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, adapt, and redistribute with attribution.
