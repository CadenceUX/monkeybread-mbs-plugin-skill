# Changelog

## v1.3 — 2026-07-05

- **Replaced the docset pipeline with a live-site crawl.** The vendor now publishes
  every documentation page as clean markdown (`mbsplugins.eu/{FunctionName}.md`, with
  `index.md` and `component_X.md` as listing pages) — no `llms.txt` exists, but the
  markdown mirror serves the same purpose. `scripts/build_catalog.py` no longer needs a
  downloaded `MBS.docset`: it enumerates functions from the markdown listing pages and
  parses detail from the matching `.shtml` pages (the HTML is still used for detail
  because only it carries the paste-ready `fmxmlsnippet` XML examples — the `.md`
  mirror drops them). The script now fails loudly if any page can't be fetched instead
  of skipping, and takes an optional fetch-cache directory.
- **Catalog grew from 7,370 to 7,807 functions (245 components)**, re-derived by full
  enumeration per the catalog-accuracy rules, and verified a strict superset of v1.2
  (zero functions lost). The growth breaks down as: functions added to the plugin
  since the 16.2 docset snapshot, 39 pre-release 16.3 functions, and 266 deprecated
  functions the docset never indexed (see below). The site's `index.md` headline
  counter said 7,919 at build time; the ~112 residual is not linked from any component
  or deprecated listing page and is documented as such rather than papered over.
- **New `prerelease` flag (39 functions).** The doc site documents in-development
  plugin versions ahead of release — at build time it already carried 16.3 function
  pages while the release-notes page topped out at 16.2. These are included and tagged
  `"prerelease": true` (all verified `version_introduced: 16.3`), so Claude can answer
  about them while warning they may not be in the user's installed plugin. The MBS
  version self-check now explains that once 16.3 ships, the flags are stale-conservative
  until a rebuild.
- **New `deprecated` flag (396 functions).** Enumeration now includes the vendor's
  `deprecated.md` listing page; 266 of those functions (including the entire Calendar
  and Addressbook components) were absent from all previous catalog versions, and 130
  that still sit on component pages are now flagged. Deprecated entries parse fully
  (signature, parameters, examples) so legacy scripts can be explained and replacements
  suggested.
- **Fixed an enumeration gap for dot-less top-level functions** (`Trace`, `IsError`,
  `ClearRegistration`, `CF`, ... — 38 functions). The initial markdown-link pattern
  required a dotted name, which silently dropped them; caught by diffing against the
  v1.2 catalog before publishing. Each remains its own component key, as in v1.2.
- **Live doc URL pattern switched from `.shtml` to `.md`** in SKILL.md, entry `url`
  fields, and `references/index.json` — the markdown pages are far better fetch targets.
  The "Created/last changed" documentation-freshness line is present in the `.md` pages
  too, and the catalog's build date (2026-07-05) is now the stated comparison baseline.
- **New cheap staleness signal**: `index.md`'s "Currently N functions" headline is
  stored as `site_function_count_at_build` (7,919) — one small fetch to detect that the
  vendor documented new functions, validated live (it moved from 7,370-era counts).
  Also documented `newinversionNNN.md` pages as the fastest way to see what a rebuild
  would pick up.
- `references/index.json` meta renamed/extended: `plugin_version_released_at_build`
  (replaces `plugin_version_covered`), `site_function_count_at_build`,
  `prerelease_function_count` + `prerelease_meaning`, `deprecated_function_count` +
  `deprecated_meaning`, `count_note`, `source`, and per-component `prerelease_count` /
  `deprecated_count`.
- Status counts re-derived: `free` 2,553 / `licensed` 4,682 / `unknown_license` 572
  (now across 38 components; Llama joins the mostly-unmarked list).
- README fixes: brand name corrected to the one-word form "CadenceUX", installation now
  leads with the double-click `.skill` method, attribution line added to SKILL.md's
  Licence section.

## v1.2 — 2026-06-25

- **Fixed misleading `licensed` status description.** SKILL.md, README.md, and
  the frontmatter description previously implied a `licensed` function requires
  the base plugin to be registered in order to work at all. Confirmed against
  the vendor's own [Free Tier announcement](https://www.mbsplugins.de/archive/2023-01-30/Free_Tier_for_MBS_FileMaker_Pl/monkeybreadsoftware_blog_filemaker)
  that this is wrong: a `licensed` function still runs and returns a real result
  on an unregistered install — the only consequence is a periodic reminder dialog
  (surfaces every few minutes) until the plugin is registered. Rewrote the status
  table and related notes in both files to describe the nag-dialog behaviour
  instead of implying failure. The underlying `status` classification in
  `references/*.json` (derived from the vendor's "This function checks for a
  license" marker) was already correct — only the editorial explanation of what
  that marker *means* was fixed.
- **Extended to all 7,370 functions** (previously free-only, 2,408 functions).
  Every entry now carries a `status` field instead of a bare `free` boolean:
  `free` (2,408), `licensed` (4,406), or `unknown_license` (556).
- The 556 functions with no free/licensed marker on the vendor's doc page were
  investigated rather than guessed at: fetched a live page
  (`mbsplugins.eu/CNContactName.shtml`) to confirm the marker is missing on the
  vendor's own site too, not a stale-docset artifact. Concentrated in 37
  components — mostly CURL (245), XL (102), Overlay (39), MapView (23),
  WebView (18). Cross-checked the vendor's pricing page
  (`monkeybreadsoftware.com/filemaker/pricing.shtml`) to see if licensing tier
  explained the gap — it doesn't (pricing tiers only cover DynaPDF/XL/Saxon
  add-ons, not a general free/licensed split) — so these stay `unknown_license`
  rather than being assigned a guessed status.
- Added `requires_addon` at the component level for **DynaPDF**, **XL**, and
  **Saxon** — these need a separate paid license beyond the base MBS plugin
  registration (DynaPDF $249–$1,599 tiers + PDF/A add-on; LibXL $219/platform
  or $1,199 Enterprise; Saxon-PE $325/yr or Saxon-EEV $800/yr), per the vendor's
  pricing page. No other component carries this flag.
- Fixed a grouping bug found during this rebuild: the vendor's own docset has a
  handful of mis-cased component prefixes (`Webview.X` alongside `WebView.X`,
  `Progressdialog.X` alongside `ProgressDialog.X`) that are the same logical
  component, not distinct ones. These previously collided on the same output
  filename slug and silently overwrote each other. Now grouped case-insensitively
  with the majority casing kept as the canonical component name (233 components).
- **Replaced one-file-per-component with 20 bin-packed group files**
  (`group-01.json`–`group-20.json`) after the broader function set pushed the
  release zip to 241 files — over the ~200-file practical ceiling on Claude.ai
  skill zip uploads (documented in `cadenceux-skill-creator`'s own v1.2 release;
  no official Anthropic-published number exists, but it's a real-world install
  failure others have hit). `scripts/build_catalog.py` now serializes each
  component's data, sorts by size, and greedily assigns each component to the
  currently-lightest group — keeping group files reasonably balanced (808KB–3MB
  each here) instead of one-file-per-component, which let single huge components
  like DynaPDF (2.9MB) sit alongside near-empty single-function components and
  drove file count past the ceiling.
- `references/index.json` now maps each component to a `group-NN.json` file
  rather than a `<component>.json` file or the old `free_function_count` /
  `skipped_licensed_count` fields — it gained `status_meaning`, `status_counts`,
  `addon_components`, and per-component `status_counts`. Lookup path in
  `SKILL.md`/`README.md` is index → group file → component → function.
- Group-file assignment is **not stable across rebuilds** — recomputed from
  scratch each time based on current component sizes. A future rebuild changing
  which group a component lands in is expected, not a bug.
- Total file count: 25 (20 group files + index.json + SKILL.md + README.md +
  CHANGELOG.md + scripts/build_catalog.py), comfortably under the ~200-file
  ceiling with room for the catalog to keep growing. Catalog size grew from
  ~5MB to ~20MB unzipped (DynaPDF, CURL, XL, GMImage are the largest components
  at 1–3MB each).
- Removed the now-unused `slug()` helper from `build_catalog.py`.

## v1.1 — 2026-06-23

- Added a **version self-check**: at the start of a session, Claude fetches the
  vendor's live release notes page
  (`https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml`), reads the
  topmost "Release notes for version X.X" heading, and compares it against this
  catalog's `plugin_version_covered` (16.2). If the live plugin version is newer,
  Claude surfaces a one-time advisory notice rather than silently working from a
  stale catalog. Mirrors the version-check pattern used in `claris-filemaker-pro`,
  adapted to point at MBS's own release notes page since this skill has no
  separate GitHub-hosted release of its own.
- Added a **version drift** note for per-function live lookups: if a function's
  live doc page shows a version higher than 16.2, that function was added after
  this catalog was built.
- Added `release_notes_url` to `references/index.json`, emitted by
  `scripts/build_catalog.py`.
- No changes to the underlying function data — still 2,408 free functions across
  188 components, MBS Plugin version 16.2.

## v1.0 — 2026-06-23

Initial release.

- Reflects **MBS Plugin version 16.2** — detected automatically from the highest
  `newinversionNNN.html` page in the docset (there's no single version field in
  `Info.plist` or `index.html`); stored as `plugin_version_covered` in
  `references/index.json`.
- Built `references/index.json` + 188 per-component JSON files from the vendor's
  `MBS.docset` (Dash docset shipped with the MBS FileMaker Plugin).
- Scope: **free-to-use functions only** — 2,408 of the docset's 7,370 total functions.
  The other ~4,406 require a paid MBS license and check for it at call time; they are
  excluded from this catalog rather than documented with unverifiable behavior. ~556
  pages had no free/licensed marker at all (mostly edge-case or non-standard layout
  pages) and were excluded as unparsed rather than guessed at.
- Each entry includes: `signature`, `description`, structured `parameters` (with an
  `optional` flag reconciled against the vendor's parameter table, where present),
  `result`, `version_introduced`, `compatibility` (macOS/Windows/Linux/Server/iOS SDK),
  `examples` (paired plain-text calculation + `fmxmlsnippet` XML, verbatim from the
  vendor's doc page where available), `see_also`, and a live `url` back to
  `mbsplugins.eu` for cross-checking.
- Included `scripts/build_catalog.py` so the catalog can be regenerated from a newer
  `MBS.docset` after a plugin update.
- Known gap, deliberately deferred: licensed functions are not yet catalogued. A v1.1
  can extend the same pipeline to cover them for users holding an MBS license.
