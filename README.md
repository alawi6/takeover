# Brandstofprijzen live dashboard

Dit project werkt zo:

1. `update_prices.py` haalt elke run de huidige officiële FOD-PDF op.
2. Het script leest de geldigheidsdatum en prijzen uit de PDF.
3. Het script schrijft of overschrijft die dag in `dataset.csv`.
4. `index.html` leest automatisch `dataset.csv` en toont de grafiek.
5. GitHub Actions draait dit automatisch twee keer per dag.

## Belangrijke mapping

Deze mapping is afgestemd op jouw bestaande CSV:

- `Benzine 95` = **Benzine 95 RON E10 aan de pomp**
- `Benzine 98` = **Benzine 98 RON E5 aan de pomp**
- `Diesel` = **Diesel B7 aan de pomp**
- `Stookolie (bestelling > 2.000 liter)` = **Gasolie vanaf 2000 l**

## Zo zet je het live

1. Maak een nieuwe GitHub-repo.
2. Upload alle bestanden uit deze map naar de root van die repo.
3. Zet GitHub Pages aan:
   - Settings
   - Pages
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/root`
4. Open daarna je site op:
   - `https://JOUWNAAM.github.io/REPO_NAAM/`

## Belangrijk voor Pages

GitHub Pages toont standaard `index.html`. Daarom moet het dashboardbestand `index.html` heten.

## Handig testen

Je kan lokaal testen met:

```bash
pip install -r requirements.txt
python update_prices.py
python -m http.server 8000
```

Open daarna `http://localhost:8000`.

## Bronnen

- FOD Economie publiceert het dagelijkse officiële tarief en linkt naar het actuele tarief-PDF.
- Statbel verwijst voor het overzicht van de officiële tarieven.
