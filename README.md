# Větev na větvi

Osobní web — terénní poznámky o živých věcech a příbězích, které vyprávějí.
Statické HTML v designovém systému **Větev na větvi** (cream, lesní zeleň + terakota,
Merriweather / Inter / Fira Code, motiv větve a uzlů). Žádné závislosti, žádný build.

## Obsah

| Soubor | Co to je |
| --- | --- |
| `index.html` | Rozcestník (hlavní strana) |
| `wetware-ch1-jsi-sloveso.html` | WETWARE · Kapitola první — *Jsi sloveso* (hotová kapitola) |
| `o-mne.html`, `wetware.html`, `pribehy.html`, `lusteni.html`, `zpetna-vazba.html` | Zatím zástupné stránky („připravuje se") |
| `wetware-biochemie.html`, `wetware-neurobiologie.html`, `wetware-fyziologie.html`, `wetware-molekularni-biologie.html` | Podvětve Wetware — zatím zástupné |
| `404.html` | Stránka pro nenalezené adresy |
| `.nojekyll` | Řekne GitHub Pages, ať HTML servíruje tak, jak je (bez Jekyll) |

Všechny odkazy jsou **relativní**, takže web funguje i v podadresáři `/vetev-na-vetvi/`.

## Publikace přes GitHub Pages

1. Vytvoř na GitHubu repozitář **`vetev-na-vetvi`** (může být veřejný).
2. Nahraj do něj **obsah tohoto adresáře** (ne složku samotnou — soubory ať jsou v kořeni repozitáře).
3. V repozitáři otevři **Settings → Pages**.
4. **Source:** *Deploy from a branch* → branch **`main`** → složka **`/ (root)`** → **Save**.
5. Za chvíli poběží na `https://<tvé-uživatelské-jméno>.github.io/vetev-na-vetvi/`.

### Přes příkazovou řádku (git)

```bash
# v rozbaleném adresáři:
git init
git add .
git commit -m "Větev na větvi — první verze webu"
git branch -M main
git remote add origin https://github.com/<tvé-jméno>/vetev-na-vetvi.git
git push -u origin main
```

Repozitář `vetev-na-vetvi` je potřeba na GitHubu nejdřív založit (prázdný, bez README),
pak spustit `git push`. GitHub Pages se zapíná v **Settings → Pages** (viz výše).

## Až budeš chtít pokračovat

Zástupné stránky stačí přepsat obsahem — názvy souborů i odkazy už sedí.
`zpetna-vazba.html` se dá klidně nahradit odkazem `mailto:` nebo formulářem.
