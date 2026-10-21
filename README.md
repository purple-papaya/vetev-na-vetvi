# Větev na větvi

Osobní web — terénní poznámky o živých věcech a příbězích, které vyprávějí.
Statické HTML v designovém systému **Větev na větvi** (cream, lesní zeleň + terakota,
Merriweather / Inter / Fira Code, motiv větve a uzlů). Žádné závislosti, žádný build.

## Struktura repozitáře

```
index.html            rozcestník (hlavní strana) — musí zůstat v kořeni (GitHub Pages)
404.html               stránka pro nenalezené adresy — musí zůstat v kořeni
favicon.svg            ikona v záložce prohlížeče (motiv větve) — odkazuje ji každá stránka
.nojekyll               řekne GitHub Pages, ať HTML servíruje tak, jak je (bez Jekyll)
css/
  base.css               sdílené proměnné (barvy, typo) + reset — používá každá stránka
  home.css                grove/větvová navigace + chrome — sdílí index.html a Wetware hub
  wetware.css             doplňky pro Wetware hub (rozvrh kapitol, stavové štítky)
  stub.css                layout zástupných stránek (pages/*.html stub + 404.html)
  chapter.css              styly kapitoly Biochemie (pages/wetware-ch1-jsi-sloveso.html)
  farmakologie-ch1.css     styly kapitoly Farmakologie — „Lék je vlna“ (vlastní design)
  neurobiologie-ch1.css    styly kapitoly Neurobiologie — „Jak se sůl naučila říkat já“ (vlastní design)
  fyziologie-ch1.css       styly kapitoly Fyziologie — „Moře pod kůží“ (design neurobiologie + posuvníky)
  wetware-kapitola.css     sdílené styly kapitol Molekulární biologie, Imunologie, Vývojové biologie
                            a Endokrinologie (design „Moře pod kůží“ + legendy simulací a ilustrace);
                            používá je i článek na blogu
assets/
  icons.svg                SVG sprite se dvěma značkami (#logo-mark, #logo-mark-sm),
                            vykreslované přes <use> místo kopírování SVG na každou stránku
  og/                      náhledové obrázky pro sdílení (1200×630, jeden na kapitolu a článek) a logo
tools/
  seo.py                   metadata pro vyhledávače a jazykové modely (viz níž)
sitemap.xml, robots.txt  mapa webu a pravidla pro roboty (generuje tools/seo.py)
llms.txt, llms-full.txt  přehled a plné texty pro jazykové modely (generuje tools/seo.py)
pages/
  wetware.html             Wetware hub — rozcestník všech podvětví a jejich kapitol
  wetware-ch1-jsi-sloveso.html          Biochemie · Kapitola první — Jsi sloveso (hotová kapitola)
  wetware-farmakologie-ch1-lek-je-vlna.html   Farmakologie · Kapitola první — Lék je vlna (hotová kapitola)
  wetware-neurobiologie-ch1-jak-se-sul-naucila-rikat-ja.html   Neurobiologie · Kapitola první — Jak se sůl naučila říkat já (hotová kapitola)
  wetware-fyziologie-ch1-more-pod-kuzi.html   Fyziologie · Kapitola první — Moře pod kůží (hotová kapitola)
  wetware-molekularni-biologie-ch1-cteni-bez-ctenare.html   Molekulární biologie · Kapitola první — Čtení bez čtenáře (hotová kapitola)
  wetware-imunologie-ch1-darwin-v-mizni-uzline.html   Imunologie · Kapitola první — Darwin v mízní uzlině (hotová kapitola)
  wetware-vyvojova-biologie-ch1-telo-ktere-se-postavilo-samo.html   Vývojová biologie · Kapitola první — Tělo, které se postavilo samo (hotová kapitola)
  wetware-endokrinologie-ch1-dopis-pro-vsechny.html   Endokrinologie · Kapitola první — Dopis pro všechny (hotová kapitola)
  blog.html                Blog — rozcestník kratších textů mezi kapitolami
  blog-spad-prah-smycka.html   Blog · Spád, práh, smyčka — co spojuje všech osm prvních kapitol
  o-mne.html, pribehy.html, lusteni.html, zpetna-vazba.html                 zástupné stránky
  wetware-biochemie.html, wetware-neurobiologie.html, wetware-fyziologie.html,
  wetware-molekularni-biologie.html, wetware-farmakologie.html,
  wetware-imunologie.html, wetware-vyvojova-biologie.html,
  wetware-endokrinologie.html               podvětve Wetware — krátký popis a odkaz na první kapitolu
```

Odkazy jsou relativní vůči každé stránce (`pages/*.html` odkazují zpět přes `../`),
takže web funguje i v podadresáři `/vetev-na-vetvi/`. `index.html` a `404.html` zůstávají
v kořeni repozitáře — GitHub Pages je odsud vyžaduje (rozcestník i vlastní 404 stránka
fungují jen tehdy, když leží přímo v publikované složce).

## Vyhledávače a jazykové modely

Metadata všech stránek spravuje `tools/seo.py` (jen standardní knihovna Pythonu). Po přidání
nebo úpravě stránky ho spusť z kořene repozitáře:

```bash
python3 tools/seo.py
```

- **Nová stránka**: přidej ji do slovníku `PAGES` v `tools/seo.py` (titulek, popis, u kapitol témata
  a anglické shrnutí). Stránky, které tam chybí, skript vypíše a nechá beze změny.
- **Co se generuje**: v hlavičce každé stránky blok mezi komentáři `seo:begin` a `seo:end`
  (titulek, popis, kanonická adresa, Open Graph, strukturovaná data JSON-LD včetně častých otázek
  a zdrojů kapitol) a v kořeni `sitemap.xml`, `robots.txt`, `llms.txt` a `llms-full.txt`.
  Blok v hlavičce needituj ručně, při dalším spuštění se přepíše.
- **Zástupné stránky** (O mně, Příběhy, Luštění, Zpětná vazba) a 404 mají `noindex`. Až dostanou
  obsah, změň v `PAGES` jejich `kind` ze `stub` na vhodný typ.
- **Adresa webu** je `https://vetevnavetvi.cz/` (proměnná `SITE_URL`). Kdyby se web přestěhoval,
  změň ji a skript spusť znovu.
- **Data publikace a úpravy** se berou z historie gitu. Commity, jejichž zpráva začíná `SEO:`,
  se nepočítají, takže úprava metadat stránku „neomladí“.
- **Mapa webu** je odkázaná z `robots.txt`. Rychlejší je ale odeslat ji i ručně v Google Search Console
  a Bing Webmaster Tools (`https://vetevnavetvi.cz/sitemap.xml`).

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
