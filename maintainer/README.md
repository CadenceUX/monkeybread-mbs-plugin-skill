# Maintaining the MBS catalog

Not part of the installed skill's instructions. These tools rebuild `references/` from the
vendor's documentation site. Run them in Claude Code or a local Python environment with the
`bs4` (BeautifulSoup) package and network access to `mbsplugins.eu`.

```bash
python3 maintainer/build_catalog.py references/ /path/to/fresh-cache
```

- The second argument is a fetch cache, so an interrupted run doesn't refetch every page. Use a
  fresh directory when rebuilding for a new plugin version; cached pages are never revalidated.
  A cold crawl fetches around 8,000 pages and takes 20 to 40 minutes.
- The script reads the latest released version from the release notes page, enumerates
  functions from the component and deprecated pages, and sets `status`, `prerelease` and
  `deprecated` per function. It exits 1, listing the pages, if any function page can't be
  fetched.
- Examples: the vendor's pages carry each example as an `fmxmlsnippet`. `render_script.py`
  turns it into readable script steps; the XML is not shipped. With Claris ADT, scripts go into
  the file directly, so clipboard XML is never needed.
- `version` in `index.json` is read from the skill's `VERSION` file, so bump `VERSION` first.
- Add-on licence text (`ADDON_COMPONENTS`) deliberately carries no prices.
- Group files are re-packed every run; don't rely on a component keeping its group number.

After a rebuild: compare `catalog_function_count` and `site_function_count_at_build` in
`index.json`, update the CHANGELOG with the plugin version and counts, re-run the evals, and
run the CadenceUX skill validator.
