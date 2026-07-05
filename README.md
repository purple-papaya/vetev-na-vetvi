# Větev na větvi

Osobní web — terénní poznámky o živých věcech a příbězích, které vyprávějí.
Statické HTML v designovém systému **Větev na větvi** (cream, lesní zeleň + terakota,
Merriweather / Inter / Fira Code, motiv větve a uzlů). Žádné závislosti, žádný build.

## Struktura repozitáře

```
index.html            rozcestník (hlavní strana) — musí zůstat v kořeni (GitHub Pages)
404.html               stránka pro nenalezené adresy — musí zůstat v kořeni
.nojekyll               řekne GitHub Pages, ať HTML servíruje tak, jak je (bez Jekyll)
css/
  base.css               sdílené proměnné (barvy, typo) + reset — používá každá stránka
  home.css                grove/větvová navigace + chrome — sdílí index.html a Wetware hub
  wetware.css             doplňky pro Wetware hub (rozvrh kapitol, stavové štítky)
  stub.css                layout zástupných stránek (pages/*.html stub + 404.html)
  chapter.css              styly kapitoly Biochemie (pages/wetware-ch1-jsi-sloveso.html)
  farmakologie-ch1.css     styly kapitoly Farmakologie — „Lék je vlna“ (vlastní design)
assets/
  icons.svg                SVG sprite se dvěma značkami (#logo-mark, #logo-mark-sm),
                            vykreslované přes <use> místo kopírování SVG na každou stránku
pages/
  wetware.html             Wetware hub — rozcestník všech podvětví a jejich kapitol
  wetware-ch1-jsi-sloveso.html          Biochemie · Kapitola první — Jsi sloveso (hotová kapitola)
  wetware-farmakologie-ch1-lek-je-vlna.html   Farmakologie · Kapitola první — Lék je vlna (hotová kapitola)
  o-mne.html, pribehy.html, lusteni.html, zpetna-vazba.html                 zástupné stránky
  wetware-biochemie.html, wetware-neurobiologie.html, wetware-fyziologie.html,
  wetware-molekularni-biologie.html, wetware-farmakologie.html               podvětve Wetware — zástupné
```

Odkazy jsou relativní vůči každé stránce (`pages/*.html` odkazují zpět přes `../`),
takže web funguje i v podadresáři `/vetev-na-vetvi/`. `index.html` a `404.html` zůstávají
v kořeni repozitáře — GitHub Pages je odsud vyžaduje (rozcestník i vlastní 404 stránka
fungují jen tehdy, když leží přímo v publikované složce).

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
