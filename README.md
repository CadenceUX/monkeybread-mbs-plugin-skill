# monkeybread-mbs-plugin

A [Claude skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for
the **MBS FileMaker Plugin** from Monkeybread Software. Claude answers from a catalog built from
the vendor's documentation, not from training data: every documented
`MBS( "Component.Function"; ... )` function with its signature, parameters, result, platform
support, version introduced, licensing status and examples.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).

## What it does

- **Looks up any MBS function** through `references/index.json` (component to group file) and
  the grouped catalog files.
- **Flags licensing honestly:** every function is `free`, `licensed` (runs unregistered, with a
  reminder dialog) or `unknown_license`. DynaPDF, XL and Saxon need a separate add-on licence.
- **Flags deprecated functions** and points to the replacement, and checks platform support
  (macOS, Windows, Linux, Server, iOS SDK) before suggesting a function.
- **Readable examples:** the vendor's examples as FileMaker script steps. With the Claris Agentic
  Development Toolkit (ADT) installed, Claude writes them into your file directly; there's no
  clipboard XML.
- **Stays current:** checks Monkeybread's release notes and this repo's `VERSION` once a
  session, and tells you when either is newer.

Built against MBS Plugin 16.4 on 2026-10-11. Counts live in `references/index.json`.

## Install

**Claude Code** (from the `cadenceux` plugin marketplace):

```bash
claude plugin marketplace add https://github.com/CadenceUX/cadenceux-skills.git
claude plugin install monkeybread-mbs-plugin@cadenceux
```

**claude.ai and Cowork:** Customize → Plugins → Add marketplace from GitHub →
`CadenceUX/cadenceux-skills`, then install **monkeybread-mbs-plugin**.

**Claude desktop app (macOS):** download `monkeybread-mbs-plugin-v2.0.0.skill` from the
[latest release](https://github.com/CadenceUX/monkeybread-mbs-plugin-skill/releases) and double-click it.

**Claude.ai in a browser, as a single skill:** Customize → Skills → upload the release `.zip`.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Lookup method, status rules, version checks |
| `references/index.json` | Component to group-file map, counts, build metadata |
| `references/group-NN.json` | The catalog, grouped by size |
| `evals/evals.json` | Test cases |
| `maintainer/` | Catalog build tools (not loaded by the skill) |

## Related skills

Part of the CadenceUX FileMaker set: [goya-be-plugin](https://github.com/CadenceUX/goya-be-plugin-skill),
[beezwax-bbox-plugin](https://github.com/CadenceUX/beezwax-bbox-plugin-skill) and
[claris-filemaker-pro](https://github.com/CadenceUX/claris-filemaker-pro-skill).

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use it, fork it, adapt it. Attribute it.

MBS Plugin documentation © Monkeybread Software; this catalog summarises it for lookup and links
every entry back to the vendor's page.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
