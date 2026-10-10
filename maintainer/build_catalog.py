#!/usr/bin/env python3
"""
Builds the monkeybread-mbs-plugin reference catalog from the live
mbsplugins.eu documentation site (no local docset needed).

Enumeration comes from the vendor's markdown mirror -- index.md lists every
component as component_X.md, and each component page lists every function
with a link to its doc-page stem. Function detail is parsed from the .shtml
HTML pages (same fixed layout the old Dash-docset pipeline used) because
only the HTML carries the examples (vendor fmxmlsnippet XML, rendered to readable
script steps by render_script.py; the XML itself is not shipped) (the .md
mirror drops the copy-box textarea that holds them).

Output is unchanged in shape from v1.2: components bin-packed by size into
NUM_GROUPS grouped JSON files under references/ (group-01.json, ...), plus
a references/index.json manifest. Grouped rather than one-file-per-component
to stay well under the ~200-file practical ceiling on Claude.ai skill zip
uploads.

Usage:
    python3 build_catalog.py /path/to/output/references [/path/to/cache]

The optional cache directory stores fetched pages so an interrupted or
repeated run doesn't refetch ~8,000 pages. Delete the cache (or pass a
fresh directory) to force a full refetch for a new plugin version.

Every function gets a status field:
  - "free"            -- page says "This function is free to use."
  - "licensed"        -- page says "This function checks for a license."
  - "unknown_license" -- page has neither marker (a vendor doc-template
                          gap; don't guess).

Every function also gets a prerelease flag: the site documents functions
for in-development plugin versions ahead of their release (e.g. 16.3 pages
were live while the release-notes page still topped out at 16.2). A
function is tagged "prerelease": true when its version_introduced is
higher than the latest released version found on the vendor's release
notes page at build time.

Every function also gets a deprecated flag, from the vendor's deprecated.md
listing page. Deprecated functions still exist and are documented -- some
remain on their component page, others are listed only on deprecated.md --
so both sources are enumerated and merged.
"""
from render_script import render, strip_xml, trim_description
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://www.mbsplugins.eu"
RELEASE_NOTES_URL = "https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml"
USER_AGENT = "CadenceUX-skill-catalog-builder (darrin@cadenceux.com.au)"

FREE_MARKER = "This function is free to use."
LICENSED_MARKER = "This function checks for a license."

# Number of grouped reference files to bin-pack components into. Keeps total
# skill file count well under the ~200-file practical ceiling on Claude.ai
# skill zip uploads, regardless of how many components the site lists.
NUM_GROUPS = 20

MAX_WORKERS = 8
FETCH_RETRIES = 4

# Components confirmed (via the vendor's pricing page) to require a separate
# paid add-on beyond the base MBS plugin license -- distinct from the per-
# function free/licensed/unknown_license status.
ADDON_COMPONENTS = {
    "DynaPDF": "Requires a separate DynaPDF licence (Starter, Lite, Pro or Enterprise, plus an "
    "optional PDF/A add-on) on top of the base MBS plugin. Check current pricing with Monkeybread.",
    "XL": "Requires a separate LibXL licence on top of the base MBS plugin. "
    "Check current pricing with Monkeybread.",
    "Saxon": "Requires a separate Saxon-PE or Saxon-EE licence on top of the base MBS plugin. "
    "Check current pricing with Monkeybread.",
}


def fetch(url, cache_dir=None, cache_key=None):
    if cache_dir is not None and cache_key is not None:
        cache_file = cache_dir / cache_key
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8")
    last_err = None
    for attempt in range(FETCH_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
            if cache_dir is not None and cache_key is not None:
                cache_file = cache_dir / cache_key
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(body, encoding="utf-8")
            return body
        except Exception as e:  # noqa: BLE001 -- retry any transport error
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed after {FETCH_RETRIES} attempts: {url}: {last_err}")


def version_tuple(version_str):
    """'16.2' -> (16, 2). Returns None if the string isn't a plain dotted number."""
    if not version_str:
        return None
    m = re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version_str.strip())
    if not m:
        return None
    return tuple(int(x) for x in version_str.strip().split("."))


def latest_released_version():
    """Topmost 'Release notes for version X.Y' heading on the vendor's release
    notes page = the latest *shipped* plugin version. The doc site itself runs
    ahead of this (it documents in-development versions), which is exactly why
    the prerelease flag exists."""
    html = fetch(RELEASE_NOTES_URL)
    m = re.search(r"Release notes for version ([0-9.]+)", html)
    if not m:
        raise RuntimeError("could not find a 'Release notes for version' heading -- page layout changed?")
    return m.group(1)


def site_function_count(index_md):
    """index.md opens with 'Currently NNNN functions ...' -- the cheap one-fetch
    staleness signal the SKILL.md documents. Store it so future drift checks
    have a baseline."""
    m = re.search(r"Currently\s+([0-9,]+)\s+functions", index_md)
    return int(m.group(1).replace(",", "")) if m else None


FUNC_LINK = re.compile(r"\[([A-Za-z0-9.]+)\]\(([A-Za-z0-9]+)\.md\)")


def function_links(md):
    """A real function link's stem is its name with any dots removed --
    [DynaPDF.Parser.Content](DynaPDFParserContent.md), or the dot-less
    top-level functions like [Trace](Trace.md). The name==stem rule filters
    out prose links to component_X.md / newinversionNNN.md / index pages."""
    out = {}
    for name, page_stem in FUNC_LINK.findall(md):
        if name.replace(".", "").lower() == page_stem.lower():
            out[name] = page_stem
    return out


def enumerate_functions(cache_dir):
    """index.md -> component_X.md pages, plus deprecated.md ->
    ({function name: stem}, component page stems, site headline count,
    set of deprecated function names)."""
    index_md = fetch(f"{BASE_URL}/index.md", cache_dir, "md/index.md")
    claimed_count = site_function_count(index_md)

    component_stems = sorted(set(re.findall(r"\(component_([A-Za-z0-9]+)\.md\)", index_md)))
    if not component_stems:
        raise RuntimeError("no component_X.md links found in index.md -- page layout changed?")

    functions = {}  # name -> stem

    def fetch_component(stem):
        return stem, fetch(f"{BASE_URL}/component_{stem}.md", cache_dir, f"md/component_{stem}.md")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for future in as_completed([pool.submit(fetch_component, s) for s in component_stems]):
            _, md = future.result()
            functions.update(function_links(md))

    # Deprecated functions are documented too -- some still appear on their
    # component page, others only on the deprecated listing. Enumerate both
    # and remember which names are deprecated so entries can be flagged.
    deprecated_md = fetch(f"{BASE_URL}/deprecated.md", cache_dir, "md/deprecated.md")
    deprecated_links = function_links(deprecated_md)
    deprecated_names = set(deprecated_links)
    functions.update(deprecated_links)

    return functions, component_stems, claimed_count, deprecated_names


# --- .shtml page parsing (unchanged layout from the v1.2 docset pipeline) ---


def text_or_none(node):
    if node is None:
        return None
    t = node.get_text(" ", strip=True)
    return t or None


def parse_platform_table(soup):
    """The table headed Component | Version | macOS | Windows | Linux | Server | iOS SDK."""
    for t in soup.find_all("table"):
        header_row = t.find("tr")
        if header_row is None:
            continue
        header_cells = [c.get_text(strip=True) for c in header_row.find_all(["td", "th"])]
        if "Component" in header_cells and "Version" in header_cells:
            rows = t.find_all("tr")
            if len(rows) < 2:
                return None, {}
            cells = rows[1].find_all("td")
            if len(cells) < 7:
                return None, {}
            version = text_or_none(cells[1])

            def yes(cell):
                return "Yes" in cell.get_text()

            compat = {
                "macos": yes(cells[2]),
                "windows": yes(cells[3]),
                "linux": yes(cells[4]),
                "server": yes(cells[5]),
                "ios_sdk": yes(cells[6]),
            }
            return version, compat
    return None, {}


def parse_signature(soup):
    proto = soup.find("div", id="PrototypeSmall")
    if proto is None:
        return None
    sig = proto.get_text(" ", strip=True)
    sig = sig.replace("More", "").strip()
    sig = re.sub(r"\s+", " ", sig)
    return sig


def parse_parameters(soup):
    h3 = soup.find("h3", string="Parameters")
    if h3 is None:
        return []
    table = h3.find_next("table")
    if table is None:
        return []
    rows = table.find_all("tr")
    if not rows:
        return []
    header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
    has_flags = "Flags" in header_cells

    params = []
    for tr in rows[1:]:
        cells = tr.find_all("td")
        if not cells:
            continue
        name = text_or_none(cells[0]) or ""
        description = text_or_none(cells[1]) if len(cells) > 1 else None
        example = text_or_none(cells[2]) if len(cells) > 2 else None
        optional = False
        if has_flags and len(cells) > 3:
            optional = "Optional" in cells[3].get_text()
        params.append(
            {
                "name": name,
                "description": description,
                "example": example,
                "optional": optional,
            }
        )
    return params


def parse_simple_section(soup, heading):
    h3 = soup.find("h3", string=heading)
    if h3 is None:
        return None
    parts = []
    for sib in h3.next_siblings:
        if getattr(sib, "name", None) == "h3":
            break
        if getattr(sib, "name", None) == "table":
            break
        if hasattr(sib, "get_text"):
            t = sib.get_text(" ", strip=True)
            if t:
                parts.append(t)
        elif isinstance(sib, str) and sib.strip():
            parts.append(sib.strip())
    return " ".join(parts).strip() or None


def parse_examples(soup):
    h3 = soup.find("h3", string="Examples")
    if h3 is None:
        return []
    examples = []
    label = None
    for sib in h3.next_siblings:
        if getattr(sib, "name", None) == "h3":
            break
        if getattr(sib, "name", None) == "p":
            label = sib.get_text(" ", strip=True)
        if getattr(sib, "name", None) == "div" and "code-box" in (sib.get("class") or []):
            for btn in sib.find_all("button"):
                btn.decompose()
            textarea = sib.find("textarea")
            xml_code = textarea.get_text().strip() if textarea else None
            if textarea:
                textarea.decompose()
            text_code = sib.get_text("\n", strip=True)
            try:
                script = render(xml_code) if xml_code else (text_code or "")
            except Exception:
                script = text_code or ""
            examples.append({"label": label, "script": script})
            label = None
    return examples


def parse_see_also(soup):
    h3 = soup.find("h3", string="See also")
    if h3 is None:
        return []
    ul = h3.find_next("ul")
    if ul is None:
        return []
    return [a.get_text(strip=True) for a in ul.find_all("a")]


def parse_function_page(html, name, stem, released_tuple, deprecated):
    if FREE_MARKER in html:
        status = "free"
    elif LICENSED_MARKER in html:
        status = "licensed"
    else:
        status = "unknown_license"

    soup = BeautifulSoup(html, "html.parser")

    h2 = soup.find("h2")
    page_name = h2.get_text(strip=True) if h2 else name

    short_desc = None
    if h2:
        p = h2.find_next("p")
        if p:
            short_desc = p.get_text(" ", strip=True)

    version, compat = parse_platform_table(soup)
    introduced = version_tuple(version)
    prerelease = bool(introduced and released_tuple and introduced > released_tuple)

    return {
        "name": page_name,
        "signature": parse_signature(soup),
        "description": trim_description(strip_xml(parse_simple_section(soup, "Description") or short_desc)),
        "parameters": parse_parameters(soup),
        "result": strip_xml(parse_simple_section(soup, "Result")),
        "version_introduced": version,
        "prerelease": prerelease,
        "deprecated": deprecated,
        "compatibility": compat,
        "examples": parse_examples(soup),
        "see_also": parse_see_also(soup),
        "status": status,
        "url": f"{BASE_URL}/{stem}.md",
    }


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)

    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)

    released = latest_released_version()
    released_tuple = version_tuple(released)
    print(f"Latest released plugin version (release notes page): {released}")

    functions, component_stems, claimed_count, deprecated_names = enumerate_functions(cache_dir)
    print(
        f"Enumerated {len(functions)} unique functions from {len(component_stems)} component pages "
        f"+ deprecated.md ({len(deprecated_names)} deprecated)"
    )
    if claimed_count is not None:
        print(f"index.md claims 'Currently {claimed_count} functions'")

    # Same mis-cased-component-prefix normalisation as v1.2 (the vendor's own
    # site has e.g. "Webview.X" alongside "WebView.X"): group case-
    # insensitively and pick the most common casing as the display name.
    raw_component_counts = defaultdict(lambda: defaultdict(int))
    for name in functions:
        raw_component = name.split(".")[0]
        raw_component_counts[raw_component.lower()][raw_component] += 1
    canonical_name = {
        lower: max(variants.items(), key=lambda kv: kv[1])[0]
        for lower, variants in raw_component_counts.items()
    }

    by_component = defaultdict(list)
    status_counts = {"free": 0, "licensed": 0, "unknown_license": 0}
    prerelease_count = 0
    deprecated_count = 0
    failures = []

    def fetch_and_parse(item):
        name, stem = item
        html = fetch(f"{BASE_URL}/{stem}.shtml", cache_dir, f"shtml/{stem}.shtml")
        return name, parse_function_page(html, name, stem, released_tuple, name in deprecated_names)

    items = sorted(functions.items())
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_and_parse, item): item for item in items}
        for future in as_completed(futures):
            name, stem = futures[future]
            try:
                _, entry = future.result()
            except Exception as e:  # noqa: BLE001
                failures.append((name, str(e)))
                continue
            component = canonical_name[name.split(".")[0].lower()]
            by_component[component].append(entry)
            status_counts[entry["status"]] += 1
            if entry["prerelease"]:
                prerelease_count += 1
            if entry["deprecated"]:
                deprecated_count += 1
            done += 1
            if done % 500 == 0:
                print(f"  parsed {done}/{len(items)} function pages...")

    if failures:
        print(f"FATAL: {len(failures)} function pages could not be fetched/parsed:")
        for name, err in failures[:20]:
            print(f"  {name}: {err}")
        sys.exit(1)

    index = {
        "skill": "monkeybread-mbs-plugin",
        "version": (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip(),
        "plugin_name": "MBS FileMaker Plugin",
        "plugin_version_released_at_build": released,
        "site_function_count_at_build": claimed_count,
        "catalog_function_count": sum(status_counts.values()),
        "prerelease_function_count": prerelease_count,
        "prerelease_meaning": "The vendor's doc site documents functions for in-development "
        "plugin versions ahead of release. prerelease: true means the function's "
        "version_introduced was higher than plugin_version_released_at_build when this "
        "catalog was built -- it exists in the docs but may not be in the shipping plugin "
        "yet. Once that version ships, the flag is stale until the next rebuild.",
        "deprecated_function_count": deprecated_count,
        "deprecated_meaning": "Listed on the vendor's deprecated functions page "
        "(https://www.mbsplugins.eu/deprecated.md) at build time. Deprecated functions "
        "still exist and run, but the vendor recommends a replacement -- check the "
        "function's own doc page for what to use instead.",
        "count_note": "catalog_function_count is derived by enumerating every function "
        "link on the vendor's component_X.md pages plus the deprecated.md page. The "
        "site's index.md headline counter (site_function_count_at_build) is higher by a "
        "small residual not linked from any listing page; the enumerated set is a strict "
        "superset of the previous docset-based catalog and includes every function on "
        "the newest newinversionNNN.md pages.",
        "vendor": "Monkeybread Software (Christian Schmitz)",
        "source": "Live crawl of https://www.mbsplugins.eu (enumerated via the markdown "
        "mirror index.md/component_X.md, detail parsed from the .shtml pages).",
        "license": "comprehensive catalog -- every function tagged with a status field "
        "(free / licensed / unknown_license). See status_counts and status_meaning below.",
        "status_meaning": {
            "free": "Vendor doc page states this function is free to use (works unregistered).",
            "licensed": "Vendor doc page states this function checks for a license "
            "(requires the base MBS plugin to be registered).",
            "unknown_license": "Vendor doc page has neither marker. Status genuinely "
            "unconfirmed; verify against the live url before relying on this being free or licensed.",
        },
        "addon_components": ADDON_COMPONENTS,
        "url_pattern": "https://www.mbsplugins.eu/{FunctionNameWithoutDots}.md",
        "index_url": "https://www.mbsplugins.eu/index.md",
        "release_notes_url": RELEASE_NOTES_URL,
        "total_function_count": sum(status_counts.values()),
        "status_counts": status_counts,
        "components": {},
    }

    component_blobs = {}
    for component, funcs in by_component.items():
        funcs_sorted = sorted(funcs, key=lambda f: f["name"])
        status_counts_c = {"free": 0, "licensed": 0, "unknown_license": 0}
        prerelease_c = 0
        deprecated_c = 0
        for f in funcs_sorted:
            status_counts_c[f["status"]] += 1
            if f["prerelease"]:
                prerelease_c += 1
            if f["deprecated"]:
                deprecated_c += 1
        component_blobs[component] = {
            "component": component,
            "function_count": len(funcs_sorted),
            "status_counts": status_counts_c,
            "prerelease_count": prerelease_c,
            "deprecated_count": deprecated_c,
            "requires_addon": ADDON_COMPONENTS.get(component),
            "functions": funcs_sorted,
        }

    sizes = {c: len(json.dumps(b, ensure_ascii=False)) for c, b in component_blobs.items()}
    ordered = sorted(sizes, key=lambda c: -sizes[c])

    groups = [[] for _ in range(NUM_GROUPS)]
    group_sizes = [0] * NUM_GROUPS
    for component in ordered:
        lightest = group_sizes.index(min(group_sizes))
        groups[lightest].append(component)
        group_sizes[lightest] += sizes[component]

    for i, group_components in enumerate(groups):
        if not group_components:
            continue
        filename = f"group-{i + 1:02d}.json"
        group_components_sorted = sorted(group_components, key=lambda c: c.lower())
        (out_dir / filename).write_text(
            json.dumps(
                {"components": {c: component_blobs[c] for c in group_components_sorted}},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        for component in group_components_sorted:
            index["components"][component] = {
                "file": f"references/{filename}",
                "function_count": component_blobs[component]["function_count"],
                "status_counts": component_blobs[component]["status_counts"],
                "prerelease_count": component_blobs[component]["prerelease_count"],
                "deprecated_count": component_blobs[component]["deprecated_count"],
            }

    (out_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    used_groups = sum(1 for g in groups if g)
    print(f"Parsed {sum(status_counts.values())} functions across {len(by_component)} components")
    print(f"Status breakdown: {status_counts}")
    print(f"Prerelease functions (introduced after v{released}): {prerelease_count}")
    print(f"Deprecated functions (on deprecated.md): {deprecated_count}")
    if claimed_count is not None and claimed_count != sum(status_counts.values()):
        print(
            f"NOTE: index.md claims {claimed_count} functions but {sum(status_counts.values())} "
            "were enumerated from component pages -- investigate before publishing counts."
        )
    print(f"Packed into {used_groups} group files (target {NUM_GROUPS})")


if __name__ == "__main__":
    main()
