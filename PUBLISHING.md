# Publishing the supplementary materials

This public repository is the canonical source for the Quarto supplementary site. The manuscript and its administrative material remain in the separate private manuscript repository.

## Preview and render

Install Quarto 1.10.19, then preview the site from the repository root:

```sh
quarto preview .
```

Render and check the site locally with:

```sh
quarto render .
python3 check-tables.py
```

Quarto writes the website to `_site/`. The table check compares each source pipe table with its rendered HTML row and column structure, including the homepage and all 11 appendices.

## Deploy

A push to `main` builds and deploys the website to GitHub Pages. Pull requests build and validate the site, then stop before deployment. A workflow dispatch can build any selected branch; deployment runs only from `main`.
