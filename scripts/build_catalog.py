#!/usr/bin/env python3
"""
Builds the monkeybread-mbs-plugin reference catalog from a local MBS.docset.

Reads docSet.dsidx for the function index, parses every function's HTML page
(fixed Dash docset layout), and bin-packs components by size into NUM_GROUPS
grouped JSON files under references/ (group-01.json, group-02.json, ...),
plus a references/index.json manifest mapping each component to its group
file. Grouped rather than one-file-per-component to stay well under the
~200-file practical ceiling on Claude.ai skill zip uploads.

Usage:
    python3 build_catalog.py /path/to/MBS.docset /path/to/output/references

Re-run this after updating MBS.docset to refresh the catalog for a new plugin
version. Every function gets a status field:
  - "free"            -- page says "This function is free to use."
  - "licensed"         -- page says "This function checks for a license."
  - "unknown_license"  -- page has neither marker (a vendor doc-template gap,
                           confirmed present on the live site too, not just a
                           stale docset -- see v1.2 CHANGELOG). Don't guess.
"""
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup

FREE_MARKER = "This function is free to use."
LICENSED_MARKER = "This function checks for a license."

# Number of grouped reference files to bin-pack components into (see the
# packing step in main()). Keeps total skill file count well under the
# ~200-file practical ceiling on Claude.ai skill zip uploads, regardless of
# how many individual components the docset has.
NUM_GROUPS = 20

# Components confirmed (via the vendor's pricing page) to require a separate
# paid add-on beyond the base MBS plugin license -- distinct from the per-
# function free/licensed/unknown_license status.
ADDON_COMPONENTS = {
    "DynaPDF": "Requires a separate DynaPDF add-on license (Starter $249 / Lite $499 / "
    "Pro $899 / Enterprise $1,599, plus an optional PDF/A add-on) on top of the base MBS plugin.",
    "XL": "Requires a separate LibXL license ($219 per platform, or $1,199 Enterprise) "
    "on top of the base MBS plugin.",
    "Saxon": "Requires a separate Saxon subscription (Saxon-PE $325/yr or Saxon-EEV $800/yr) "
    "on top of the base MBS plugin.",
}


def text_or_none(node):
    if node is None:
        return None
    t = node.get_text(" ", strip=True)
    return t or None


def parse_platform_table(soup):
    """The second table on the page: Component | Version | macOS | Windows | Linux | Server | iOS SDK."""
    tables = soup.find_all("table")
    plat_table = None
    for t in tables:
        header_row = t.find("tr")
        if header_row is None:
            continue
        header_cells = [c.get_text(strip=True) for c in header_row.find_all(["td", "th"])]
        if "Component" in header_cells and "Version" in header_cells:
            plat_table = t
            break
    if plat_table is None:
        return None, {}

    rows = plat_table.find_all("tr")
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
            examples.append({"label": label, "text_code": text_code or None, "xml_code": xml_code})
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


def parse_function_page(path: Path, name: str, status: str):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    h2 = soup.find("h2")
    page_name = h2.get_text(strip=True) if h2 else name

    short_desc = None
    if h2:
        p = h2.find_next("p")
        if p:
            short_desc = p.get_text(" ", strip=True)

    version, compat = parse_platform_table(soup)
    signature = parse_signature(soup)
    parameters = parse_parameters(soup)
    result = parse_simple_section(soup, "Result")
    description = parse_simple_section(soup, "Description") or short_desc
    examples = parse_examples(soup)
    see_also = parse_see_also(soup)

    return {
        "name": page_name,
        "signature": signature,
        "description": description,
        "parameters": parameters,
        "result": result,
        "version_introduced": version,
        "compatibility": compat,
        "examples": examples,
        "see_also": see_also,
        "status": status,
        "url": f"https://www.mbsplugins.eu/{path.stem}.shtml",
    }


def detect_plugin_version(docs_dir: Path):
    """The docset has one newinversionNNN.html page per release (e.g. newinversion162.html
    -> 'New in version 16.2'). The highest-numbered one is the latest version this
    docset's data reflects -- there's no single version field in Info.plist or index.html."""
    best = None
    for p in docs_dir.glob("newinversion*.html"):
        m = re.match(r"newinversion(\d+)\.html$", p.name)
        if not m:
            continue
        html = p.read_text(encoding="utf-8", errors="ignore")
        title_match = re.search(r"New in version ([0-9.]+)", html)
        if not title_match:
            continue
        version_str = title_match.group(1)
        sort_key = tuple(int(x) for x in version_str.split("."))
        if best is None or sort_key > best[0]:
            best = (sort_key, version_str)
    return best[1] if best else None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    docset_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    db_path = docset_path / "Contents" / "Resources" / "docSet.dsidx"
    docs_dir = docset_path / "Contents" / "Resources" / "Documents"

    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT name, path FROM searchIndex WHERE type='Function'").fetchall()

    plugin_version_covered = detect_plugin_version(docs_dir)

    # The vendor's own docset has a handful of mis-cased component prefixes
    # (e.g. "Webview.X" alongside "WebView.X", "Progressdialog.X" alongside
    # "ProgressDialog.X") that are the same logical component, not distinct
    # ones. Group case-insensitively and pick the most common casing as the
    # canonical display name, so they land in one file instead of silently
    # colliding on the same filename slug.
    raw_component_counts = defaultdict(lambda: defaultdict(int))
    for name, _ in rows:
        raw_component = name.split(".")[0] if "." in name else name
        raw_component_counts[raw_component.lower()][raw_component] += 1
    canonical_name = {
        lower: max(variants.items(), key=lambda kv: kv[1])[0]
        for lower, variants in raw_component_counts.items()
    }

    by_component = defaultdict(list)
    status_counts = {"free": 0, "licensed": 0, "unknown_license": 0}
    skipped_missing_page = 0

    for name, rel_path in rows:
        raw_component = name.split(".")[0] if "." in name else name
        component = canonical_name[raw_component.lower()]
        page_path = docs_dir / rel_path
        if not page_path.exists():
            skipped_missing_page += 1
            continue

        html = page_path.read_text(encoding="utf-8", errors="ignore")
        if FREE_MARKER in html:
            status = "free"
        elif LICENSED_MARKER in html:
            status = "licensed"
        else:
            status = "unknown_license"

        entry = parse_function_page(page_path, name, status)
        by_component[component].append(entry)
        status_counts[status] += 1

    index = {
        "skill": "monkeybread-mbs-plugin",
        "version": "v1.2",
        "plugin_name": "MBS FileMaker Plugin",
        "plugin_version_covered": plugin_version_covered,
        "vendor": "Monkeybread Software (Christian Schmitz)",
        "license": "comprehensive catalog -- every function tagged with a status field "
        "(free / licensed / unknown_license). See status_counts and status_meaning below.",
        "status_meaning": {
            "free": "Vendor doc page states this function is free to use (works unregistered).",
            "licensed": "Vendor doc page states this function checks for a license "
            "(requires the base MBS plugin to be registered).",
            "unknown_license": "Vendor doc page has neither marker -- confirmed present on "
            "the live site too, not a stale-docset issue. Status genuinely unconfirmed; "
            "verify against the live url before relying on this being free or licensed.",
        },
        "addon_components": ADDON_COMPONENTS,
        "url_pattern": "https://www.mbsplugins.eu/{FunctionName}.shtml",
        "release_notes_url": "https://www.monkeybreadsoftware.com/filemaker/releasenotes.shtml",
        "total_function_count": sum(status_counts.values()),
        "status_counts": status_counts,
        "skipped_missing_page_count": skipped_missing_page,
        "components": {},
    }

    # Claude.ai's skill zip upload has a practical (community-reported, not
    # officially documented) ceiling around 200 files. One JSON file per
    # component would mean 233 files just for references/ -- comfortably over
    # that. Bin-pack components into a fixed number of group files instead,
    # by serialized size (greedy largest-component-into-lightest-group),
    # so file count stays small and roughly constant regardless of how many
    # components the docset has next time this is regenerated.
    component_blobs = {}
    for component, functions in by_component.items():
        functions_sorted = sorted(functions, key=lambda f: f["name"])
        status_counts_c = {"free": 0, "licensed": 0, "unknown_license": 0}
        for f in functions_sorted:
            status_counts_c[f["status"]] += 1
        blob = {
            "component": component,
            "function_count": len(functions_sorted),
            "status_counts": status_counts_c,
            "requires_addon": ADDON_COMPONENTS.get(component),
            "functions": functions_sorted,
        }
        component_blobs[component] = blob

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
                {
                    "components": {c: component_blobs[c] for c in group_components_sorted},
                },
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
            }

    (out_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    used_groups = sum(1 for g in groups if g)
    print(f"Parsed {sum(status_counts.values())} functions across {len(by_component)} components")
    print(f"Status breakdown: {status_counts}")
    print(f"Skipped {skipped_missing_page} missing pages")
    print(f"Packed into {used_groups} group files (target {NUM_GROUPS})")


if __name__ == "__main__":
    main()
