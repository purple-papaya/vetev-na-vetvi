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
  wetware-kapitola.css     sdílené styly kapitol Molekulární biologie, Imunologie, Vývojové biologie,
                            Endokrinologie a všech druhých kapitol (design „Moře pod kůží“ + legendy
                            simulací a ilustrace); používá je i článek na blogu, stránka O mně a hry
  zpetna-vazba.css         formulář zpětné vazby, seznam oprav a poznámka o soukromí
assets/
  icons.svg                SVG sprite se dvěma značkami (#logo-mark, #logo-mark-sm),
                            vykreslované přes <use> místo kopírování SVG na každou stránku
  og/                      náhledové obrázky pro sdílení (1200×630, jeden na kapitolu, článek a hru) a logo
  video/                   úvodní video webu (20 s, 1920×1080, bez zvuku) na stránce O mně: MP4 (H.264),
                            záložní WebM (VP9) pro prohlížeče bez H.264 a náhledový obrázek
tools/
  seo.py                   metadata pro vyhledávače a jazykové modely (viz níž)
  indexnow.py              pošle změněné stránky vyhledávačům přes IndexNow (viz níž)
.github/workflows/
  indexnow.yml             po každém nasazení webu spustí tools/indexnow.py
sitemap.xml, robots.txt  mapa webu a pravidla pro roboty (generuje tools/seo.py)
feed.xml                 kanál Atom s kapitolami, hrami a články (generuje tools/seo.py)
llms.txt, llms-full.txt  přehled a plné texty pro jazykové modely (generuje tools/seo.py)
b4ec072007d36d5db2a78fad120b85fb.txt            klíč pro IndexNow (název souboru = obsah); nemazat
seznam-wmt-Xjx7VmUPWoinYZqY4N3iizOrw5e6D8TY.txt   ověření webu v Seznam Webmasteru; Seznam ho občas
                                                kontroluje znovu, takže nemazat
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
  wetware-biochemie-ch2-prvni-rameno-schodiste.html   Biochemie · Kapitola druhá — První rameno schodiště (hotová kapitola)
  wetware-neurobiologie-ch2-dole-v-mezere.html   Neurobiologie · Kapitola druhá — Dole v mezeře (hotová kapitola)
  wetware-farmakologie-ch2-podani-ruky-zblizka.html   Farmakologie · Kapitola druhá — Podání ruky zblízka (hotová kapitola)
  blog.html                Blog — rozcestník kratších textů mezi kapitolami
  blog-spad-prah-smycka.html   Blog · Spád, práh, smyčka — co spojuje všech osm prvních kapitol
  o-mne.html               O mně — kdo web píše, jak kapitoly vznikají a úvodní video
  hry.html                 Hry — rozcestník miniher podle větví Wetware
  hra-*.html               24 miniher, na každou větev aspoň dvě (každá na motivy jedné kapitoly)
  zpetna-vazba.html        Zpětná vazba — formulář, seznam oprav a co se se zprávou stane (viz níž)
  pribehy.html             zástupná stránka
  wetware-biochemie.html, wetware-neurobiologie.html, wetware-fyziologie.html,
  wetware-molekularni-biologie.html, wetware-farmakologie.html,
  wetware-imunologie.html, wetware-vyvojova-biologie.html,
  wetware-endokrinologie.html               podvětve Wetware — krátký popis, odkazy na kapitoly a jejich hry
```

Odkazy jsou relativní vůči každé stránce (`pages/*.html` odkazují zpět přes `../`),
takže web funguje i v podadresáři `/vetev-na-vetvi/`. Kapitoly mají kotvy na svých částech
(`#cast-1`, `#cast-2`… v pořadí částí, `#otazky` u častých otázek, `#zdroje` u zdrojů), takže
kapitola může odkázat přímo na místo v jiné kapitole. `index.html` a `404.html` zůstávají
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
  (titulek, popis, kanonická adresa, Open Graph, odkaz na kanál, strukturovaná data JSON-LD včetně
  častých otázek, zdrojů kapitol, profilu autorky a videa) a v kořeni `sitemap.xml`, `feed.xml`,
  `robots.txt`, `llms.txt` a `llms-full.txt`. Blok v hlavičce needituj ručně, při dalším spuštění se přepíše.
- **Autorka a data pod titulkem**: pod titulek každé kapitoly, hry a článku vloží skript řádek
  „Pája · vyšlo … · aktualizováno …“ (mezi `datum:begin` a `datum:end`). Data jsou stejná jako ve
  strukturovaných datech; Google chce viditelné datum, které s nimi souhlasí.
- **Hry u kapitol**: na konec každé kapitoly vloží skript rámeček „Zahraj si“ s jejími hrami
  a na stránky větví Wetware řádek s odkazy na ně (mezi `hry:begin` a `hry:end`). Hra patří ke
  kapitole podle pole `chapter` v `PAGES`; když se hodí i k další kapitole, přidá se do pole `also`.
  Popisek si skript bere z hlavičky stránky hry.
- **Zástupná stránka** Příběhy a 404 mají `noindex`. Až Příběhy dostanou obsah, změň v `PAGES`
  jejich `kind` ze `stub` na vhodný typ.
- **Odkaz na zpětnou vazbu**: pod každou kapitolu, hru a článek vloží skript řádek „Vidíš chybu…
  Napiš mi →“ (mezi komentáři `zpetna-vazba:begin` a `zpetna-vazba:end`) a do formuláře na
  `zpetna-vazba.html` doplní seznam stránek (mezi `stranky:begin` a `stranky:end`). Obojí se při
  každém spuštění přepíše, takže nová kapitola nebo hra se v obou objeví sama.
- **Adresa webu** je `https://vetevnavetvi.cz/` (proměnná `SITE_URL`). Kdyby se web přestěhoval,
  změň ji a skript spusť znovu.
- **Data publikace a úpravy** se berou z historie gitu. Commity, jejichž zpráva začíná `SEO:`,
  se nepočítají, takže úprava metadat stránku „neomladí“.
- **Mapa webu** a kanál `feed.xml` jsou odkázané z `robots.txt`. Rychlejší je ale odeslat mapu
  i ručně v Google Search Console a Bing Webmaster Tools (`https://vetevnavetvi.cz/sitemap.xml`).
- **IndexNow**: po každém nasazení webu pošle workflow `.github/workflows/indexnow.yml` adresy
  změněných stránek Bingu, Seznamu, Yandexu a dalším vyhledávačům s IndexNow, takže si pro ně přijdou
  hned. Klíč je v souboru `b4ec072007d36d5db2a78fad120b85fb.txt` v kořeni webu (nemazat). Všechny stránky najednou pošleš
  ručně: Actions → IndexNow → Run workflow → zaškrtni „Poslat všechny stránky“. Z příkazové řádky:
  `python3 tools/indexnow.py --all` (s `--dry-run` jen vypíše adresy).
- **Ověření webu ve webmasterských nástrojích**: kód z Google Search Console, Bing Webmaster Tools
  nebo Seznam Webmaster vlož do slovníku `VERIFY` v `tools/seo.py` a skript spusť; značka se objeví
  v hlavičce úvodní stránky. Google jde ověřit i přes DNS (doménová služba), Bing umí web převzít
  z Google Search Console, Seznam potřebuje značku nebo soubor.
- **Roboti jazykových modelů**: web pouští všechny, i vyhledávání s AI (OAI-SearchBot pro ChatGPT,
  Claude-SearchBot, PerplexityBot) a roboty, kteří sbírají texty pro trénování modelů (GPTBot,
  ClaudeBot, Google-Extended…). Kdyby texty neměly sloužit k trénování, nastav v `tools/seo.py`
  `BLOCK_TRAINING = True`: vyhledávání to neovlivní, jen Google-Extended zároveň skryje web
  z odpovědí Gemini.
- **llms.txt** zůstává pro jazykové modely a agenty, které ho čtou. Google ho podle své dokumentace
  nepoužívá (pro AI přehledy stačí běžné SEO), škodit ale nemůže.

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

## Zpětná vazba

- **Odesílání**: formulář posílá zprávy přes [Web3Forms](https://web3forms.com/) na e-mail, ke kterému
  patří přístupový klíč. Klíč patří do atributu `data-key` u `<form id="fv-form">` v `pages/zpetna-vazba.html`.
  Klíč smí být veřejný, Web3Forms s ním počítá. Bez klíče formulář nic neodešle a napíše, že se
  odesílání teprve zapíná.
- **Uchování zpráv**: stránka slibuje, že zprávy zůstanou na serverech Web3Forms nejvýš 7 dní. Stejnou
  dobu nastav u formuláře v administraci Web3Forms, nebo text v sekci „Co se se zprávou stane“ uprav.
- **Seznam oprav**: novou opravu přidej do seznamu „Opraveno“ nahoru jako další `<li>` s datem,
  názvem stránky a jednou větou o tom, co se změnilo.
