# Rapport Goat Calendar

Ce dossier contient le rapport DevOps en LaTeX.

## Fichiers

- `rapport.tex` : rapport principal en francais.
- `diagrams/*.mmd` : sources Mermaid des schemas.
- `assets/logo_efrei.png` : logo EFREI si besoin.
- `assets/google_labs_yann.png` : capture Google Labs de Yann.
- `assets/google_labs_antonin.png` : capture Google Labs d'Antonin.
- `assets/login_page.png` : capture de la page de login.
- `assets/dashboard_page.png` : capture du dashboard.
- `assets/board_page.png` : capture du detail d'un board.

## Compilation VS Code

La configuration VS Code est dans `../.vscode`.

Prérequis systeme :

- extension VS Code `james-yu.latex-workshop`;
- Perl d'insallé sur l'ordinateur;
- distribution LaTeX installée, par exemple MiKTeX ou TeX Live (https://miktex.org/download);
- Le package `pdflatex` disponible dans le `PATH` (installable avec MiKTeX console par exemple) ;
- optionnel : `latexmk` pour les builds automatiques plus propres.

Depuis VS Code, ouvrir `report/rapport.tex`, puis lancer `LaTeX Workshop: Build LaTeX project`.

Depuis un terminal :

```powershell
cd report
pdflatex rapport.tex
pdflatex rapport.tex
```

## Mermaid

Les schemas Mermaid sont inclus comme sources dans le rapport. Pour generer des images PNG/SVG plus tard :

```powershell
npx @mermaid-js/mermaid-cli -i diagrams/architecture.mmd -o assets/architecture.png
```

Le rapport compile sans ces images Mermaid, car il inclut directement les fichiers `.mmd` en annexe.
