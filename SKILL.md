---
name: monkeybread-mbs-plugin
description: >-
  Reference for the MBS FileMaker Plugin from Monkeybread Software: every documented
  MBS( "Component.Function"; ... ) function with signature, parameters, result, platform
  support, version introduced, licensing status (free, licensed, unknown) and readable script
  examples, built from the vendor's documentation site. Use when an MBS( ... ) call appears in a
  FileMaker calculation or script, when asked about the MBS Plugin or Monkeybread Software, or
  when choosing an MBS function for a task. Not for BaseElements (BE_) or bBox (bBox_)
  functions, or for FileMaker's own built-in functions.
license: CC-BY-4.0
compatibility: >-
  Claude.ai, Claude Desktop, Cowork and Claude Code. Reading the catalog files needs file access
  or code execution; the live-doc and release checks need web fetch.
metadata:
  author: Darrin Southern, CadenceUX
  version: "2.0.1"
---

# MBS FileMaker Plugin — Reference Skill

**Vendor:** Monkeybread Software (Christian Schmitz)
**Source:** live crawl of the vendor's documentation site `mbsplugins.eu`, enumerated from
its markdown mirror (`index.md`, the `component_X.md` pages and `deprecated.md`), detail parsed
from the matching `.shtml` pages.
**Plugin version at build:** read `plugin_version_released_at_build` in `references/index.json`
(16.4 at this release, built 2026-10-11).
**Live doc URL pattern:** `https://www.mbsplugins.eu/{FunctionName}.md` (strip the dots
from the function name, e.g. `Dialog.GetFieldText` → `DialogGetFieldText.md`). The `.md`
pages are clean markdown — much better for fetching than the older `.shtml` pattern,
which still works for anything the `.md` mirror lacks.
**Live release notes (for version self-check):** `https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`

This catalog covers every MBS function linked from the vendor's component and deprecated
listing pages at build time. Counts are top-level fields of `references/index.json`
(`catalog_function_count`, `status_counts`, `deprecated_function_count`, `components`); quote
them from there, never from memory. Every entry
has a `status` field:

| Status | Meaning |
|---|---|
| `free` | Vendor doc page states the function works unregistered, no reminder dialog. |
| `licensed` | Paid-tier function. It still runs and returns a real result on an unregistered (free-tier) install — it does **not** fail or return an error. The only consequence of being unregistered is a periodic reminder dialog (per Monkeybread's own [Free Tier announcement](https://www.mbsplugins.de/archive/2023-01-30/Free_Tier_for_MBS_FileMaker_Pl/monkeybreadsoftware_blog_filemaker), it surfaces every few minutes while any licensed function is in use) until the base MBS plugin is registered. |
| `unknown_license` | Neither marker is present on the vendor's page. Genuinely unconfirmed; say so rather than guessing free or licensed. |

Two boolean flags sit alongside `status` on every entry:

- **`deprecated`** — listed on the vendor's deprecated-functions page
  (`https://www.mbsplugins.eu/deprecated.md`). These still exist and run, but the vendor
  recommends a replacement — check the function's own doc page for what to use instead,
  and steer users toward the replacement in new code. Whole components can be deprecated
  (Calendar and Addressbook are the largest — superseded by the newer Events and Contacts
  components).
- **`prerelease`** — documented by the vendor for a plugin version
  *newer than the latest shipped release* at build time. If the field is `true` on any entry
  in a future rebuild, it means the vendor's docs are ahead of what's released — tell the
  user the function may not be in their installed plugin yet, and treat the flag as
  stale-conservative once that version ships (the function simply works by then; the next
  rebuild clears it).

Three components additionally require a **separate paid add-on** beyond the base MBS
plugin registration — check `requires_addon` on the component file (also listed in
`references/index.json` under `addon_components`):

- **DynaPDF:** a DynaPDF licence (Starter, Lite, Pro or Enterprise).
- **XL:** a LibXL licence.
- **Saxon:** a Saxon-PE or Saxon-EE licence.

Prices change; send the user to Monkeybread's own pricing pages rather than quoting a figure.

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
   ios_sdk), `status`, `examples` (each a `label` plus `script`: the vendor's example
   rendered as readable FileMaker script steps), `see_also`, and `url` (the function's live `.md` doc page, for cross-checking or if
   the catalog looks stale).

The group files are large (megabytes). With code execution, search rather than read them
whole, for example `grep -n '"name": "Dialog.SetMessage"' references/group-NN.json`, then read
that entry's lines.

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
3. Compare it with this catalog's `plugin_version_released_at_build` (see `references/index.json`).
4. If the live version is higher, prepend this notice to your first response:

   > ⚠️ **MBS Plugin update available**
   > A newer MBS plugin version is out (v[X.X]). This skill's catalog was built when
   > v[catalog version] was the latest release. Functions added after the build won't be here —
   > check `https://www.mbsplugins.eu/{FunctionName}.md` for anything not found
   > locally, or update the skill when a new release ships. If any
   > entries in this catalog are tagged `prerelease: true` for the new version, treat
   > them as current now that it's shipped, and rebuild when convenient to clear the
   > flags.

5. Do not repeat the notice again in the same session.
6. If the fetch fails, times out, or the page layout has changed, skip silently —
   do not surface the error or block the user's actual question.

A cheaper secondary signal, useful when asked "is this catalog current?": fetch
`https://www.mbsplugins.eu/index.md` (one small page) and compare its "Currently N
functions" headline against `site_function_count_at_build` in
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
3. Compare with this skill's installed version (currently `"2.0.1"`)
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
If that version is higher than the catalog's `plugin_version_released_at_build` and the function isn't already tagged `prerelease`
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
3. If the "last changed" date is after 2026-10-11 (this catalog's build date) and the user's
   question concerns exact parameter behaviour or option names, mention that the live page may
   have details not reflected in the local catalog.
4. Skip this for routine lookups — only worth doing when the user asks if something is current, or
   when local catalog details seem to disagree with observed plugin behaviour.

## Finding the right component

The largest components are DynaPDF, XL, CURL, GMImage, Events, WebView, SQL, SyntaxColoring,
Window, FM, MongoDB and JSON; `references/index.json` lists all of them with their group file and
per-status counts. Group-file numbers change on every rebuild, so always resolve through
`index.json` rather than a remembered path.

## Notes on the data

- All MBS calls use the form `MBS( "Component.Function"; Param1 ; Param2 ; ... )` —
  optional trailing parameters are wrapped in `{ }` in the signature line. Top-level
  functions take the form `MBS( "FunctionName" )` with no component prefix.
- `compatibility` reflects the vendor's own per-platform support table — check it before
  suggesting a function for a Server-side script or iOS SDK app; many functions
  (e.g. most `Dialog.*`) are macOS/Windows-only and return an error on Server or iOS.
- `examples[].script` is the vendor's example as readable script steps
  (`Set Variable [ $r ; Value: MBS( ... ) ]`). To put one into a FileMaker file, write it
  through the Claris Agentic Development Toolkit (ADT) when installed (ADT's `fm-mcp-guide`
  skill covers its script tools), or enter the steps by hand. Never generate clipboard XML (`fmxmlsnippet`) for it.
- `status: "unknown_license"` is not the same as `"free"`. These functions (mostly CURL, XL, Overlay, MapView, WebView, Llama) have no licensing
  marker on the vendor's own doc page. Don't tell a user a function is free just
  because it's in this catalog — check `status` first.
- Deprecated functions were **absent** from catalog versions before v1.3 (the vendor's
  docset didn't index most of them) — their presence here is deliberate, so Claude can
  explain legacy scripts and point at replacements, not an endorsement for new code.

## Regenerating the catalog

Maintainers rebuild the catalog with the tools in `maintainer/` (Claude Code or a local Python
environment, not chat). See `maintainer/README.md`. In a user session, if the version check
shows a newer plugin, point the user at the live `.md` page for anything missing locally.

---

## Licence

This skill is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
