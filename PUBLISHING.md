# Publishing the supplementary materials

This public repository is the canonical source for the Quarto supplementary site. The manuscript remains in its separate repository.

## Current source

Edit `appendices/` in this main checkout. Treat proposal worktrees and preview copies as superseded reference material. Commit and push this repository to publish the current files.

`index.qmd` is the contents homepage. The live demonstration link opens the full-size simulation directly. `appendices/` contains Appendices A–K and the three pathway simulation submodules. `_quarto.yml` explicitly lists these 15 pages and defines their reading order.

`_superseded/` retains the original appendices, persona background pages and earlier updated drafts. These files are excluded from the published site, navigation and search. Shared media and references remain in `media/` and `references/`.

## Preview and check

Use Quarto 1.10.19:

```sh
quarto preview .
```

Render and check all source tables with:

```sh
quarto render .
uv run --no-project python check-tables.py
```

The site is generated in `_site/`. The checks require exactly the 15 current pages, preserve table rows and columns, and reject local workstation paths in published HTML.

## Publish

Commit and push source changes to `main`. The existing GitHub Actions workflow builds, checks and deploys the public site to:

https://alexrfholland.github.io/futures-supplementary-materials-site/

Pull requests build and validate without deployment. Workflow dispatch deploys only when run from `main`.
