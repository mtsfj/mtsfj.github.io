# mtsfj.github.io · site perso

Site statique, aucun build : ouvrir `index.html` suffit.

```
index.html              accueil (hero three.js + bio + articles + publications + contact), FR/EN
blog/index.html         le blog : tous les billets et articles, en cartes (FR/EN)
blog/modele.html        le modèle d'un billet (non référencé) : tous les composants de texte
articles/pinductor.html walkthrough interactif du papier Pinductor (EN)
articles/sycophancy.html article interactif du projet sycophancie (EN)
assets/site.css         la charte graphique : couleurs, polices, composants (partagée par toutes les pages)
assets/site.js          langue FR/EN, e-mail révélé au clic, BibTeX, vignettes pixel, FIG. 01
assets/street.js        la scène du hero (three.js), chargée en bas de index.html
assets/walls.js         les marges en pixels (pages avec .page, grand écran seulement)
assets/analytics.js     la mesure d'audience (éteinte tant qu'elle n'est pas configurée)
assets/                 couches de l'illustration et sprites (WebP sans perte ; un PNG neuf : python3 tools/png2webp.py assets/x.png)
sw.js                   le cache du navigateur : les fichiers versionnés (?v=) gardés d'une visite à l'autre
tools/png2webp.py       PNG → WebP sans perte, pixel pour pixel vérifié, références mises à jour
tools/fuji_aux.py        le masque exact du cerisier dans les calques du Fuji et le bord de sa pente (assets/fuji_aux.webp), pour l'aube
tools/night_far_clean.py nettoie night_far.webp (pixels de la rue mis à tort dans un plan lointain : lampadaire, bord du feuillage, barrière)
cv.pdf                  CV
favicon.png, og.png     icône et image de partage
```

## Déployer sur GitHub Pages (gratuit)

1. Créer un repo public nommé `mtsfj.github.io` (ou n'importe quel nom, l'URL sera alors `mtsfj.github.io/<nom>`).
2. Copier tout ce dossier à la racine du repo, `git push`.
3. Settings → Pages → Source : « Deploy from a branch », branche `main`, dossier `/ (root)`. En ligne en une minute.

Le fichier `.nojekyll` évite que GitHub ignore certains fichiers.

## Déployer sur Vercel / Netlify

Importer le repo, framework « Other », aucune commande de build, dossier de sortie `.`.

## Domaine perso (optionnel)

Un `.fr`/`.com` à ~10 €/an chez n'importe quel registrar, puis Settings → Pages → Custom domain (GitHub) ou Domains (Vercel). HTTPS automatique.

## Référencement

- IndexNow (Bing, Yandex, Seznam, Naver, et ce qui s'en nourrit : DuckDuckGo, Ecosia, Qwant) : la clé est le fichier `fc54a386d65d46f44c4b106c94b337c7.txt` à la racine ; après une mise en ligne, signaler les pages changées : `curl -s -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json' -d '{"host":"mtsfj.github.io","key":"fc54a386d65d46f44c4b106c94b337c7","urlList":["https://mtsfj.github.io/"]}'`.
- Chaque page a son titre, sa description, son URL canonique, ses aperçus de partage (Open Graph et Twitter, image 1200 × 630 : `og.png` pour l'accueil et le blog, `assets/og_*.jpg` pour les articles) et ses données structurées JSON-LD (accueil : site, profil, personne et publication ; blog : `Blog` et ses billets ; articles : `TechArticle`).
- `sitemap.xml` (avec les images), `robots.txt`, `blog/feed.xml` (flux RSS), `site.webmanifest`.
- Pour un nouveau billet : le mettre dans `sitemap.xml` et `blog/feed.xml`, avec son image de partage.

## Analytics

`assets/analytics.js`, chargé par toutes les pages, est éteint tant que `PROVIDER` et `ID` sont vides (en tête du fichier). Les services prévus mesurent l'audience sans cookie, donc sans bandeau de consentement : GoatCounter (gratuit pour un site perso), Plausible, Umami ou Cloudflare Web Analytics. En plus des pages vues, il compte quelques clics : l'e-mail affiché, le CV, le changement de langue, les liens sortants. Rien n'est envoyé depuis `localhost`.

## Langue

`?lang=fr` ou `?lang=en` dans l'URL force la langue ; sinon celle du navigateur (français uniquement pour un navigateur en français).

## La charte graphique

Toutes les pages chargent `assets/fonts/fonts.css`, puis `assets/site.css`, et `assets/site.js` en fin de page. Le `<style>` d'une page ne garde que ce qui lui est propre (la rue de l'accueil, les widgets d'un article).

- **Couleurs** : la rue la nuit. `--night` (fond), `--night-deep` (barre, haut de page), `--panel` (surfaces), `--paper` / `--paper-dim` (texte), `--pink` (néons : titres, étiquettes), `--sodium` (lampadaire : dates, chiffres, action principale). Cyan, vert et violet : données seulement.
- **Polices** : Silkscreen (pixel) pour les titres de page et les petites étiquettes, jamais pour du texte courant ; Inter Tight pour tout le reste ; JetBrains Mono pour le code.
- **Composants** : `.site-bar` (barre du haut), `.masthead` + `.eyebrow` + `.display` + `.lede` (en-tête de page), `.section` + `.section-head` (numéro, titre pixel, filet néon) (sections), `.split` (texte + panneau à droite), `.lead` (premier paragraphe), `.projects` / `.project` (cartes de projet), `.cta` (appel à l'action), `.skyline` (la ligne d'immeubles du bas de page), `.fig` + `.game` (FIG. 01 : quatre agents autotéliques qui se disputent une grille, chacun choisissant ses buts par progrès d'apprentissage), `.wall` (sur grand écran, les marges deviennent la rue : immeubles de matières variées et leurs fenêtres, boutiques en rez-de-chaussée, trouées de ciel et toits, parc au cerisier, sanctuaire, viaduc et son train ; généré par `assets/walls.js`, sans texte), `.metric` + `.bars-mini` (le chiffre d'un projet), `.entry-media.cover` (illustration d'un billet), `.entry` (la carte d'un billet : vignette, méta, titre, phrase, liens) dans `.entries` ou `.entries-grid`, `.badge`, `.chip`, `.btn`, `.links`, `.rows`, `.kv`, `.dated`, `.chrono` (frise), `.tile`, `.panel`, `.prose` (texte long), `.takeaway` (encadré), `.site-footer`. Chacun est décrit en une ligne dans `site.css`.

## Sections de l'accueil

- **Sommaire** : la pilule qui apparaît après la rue (`.toc`), la section lue allumée. Une nouvelle section y prend un lien vers son `id`.
- **Interventions et enseignement** (`#talks`) : une carte `.entry` par intervention, sa vignette pixel 168 × 112 dans `assets/talk_*.png`.
- **Bibliothèque** (`#library`) : trois étagères (livres, articles, cours en vidéo). Les livres et les cours viennent de `planning-assistant` (`references.json`, les livres qu'il indexe, `catalog.json` ; leurs couleurs = ses quatre domaines), les articles de ceux que citent les deux articles du site, plus ceux ajoutés à la main (Attention Is All You Need, FlashAttention). Chaque lien a été vérifié. un `<li><a class="book" …>` par texte, avec `data-title`, `data-authors`, `data-year`, `data-venue`, `data-theme-fr/en`, sa couleur (`--c`, `--c2` : le thème) et sa taille (`--h`, `--w`) ; `class="book star"` pour un classique ou un des cours les plus suivis.
- **Citer** : un bouton `.bib-copy` (`data-target` = l'id du bloc BibTeX) ; **S'abonner** : un bouton `.rss-btn` (un panneau avec l'adresse du flux).
- **Logos sur les façades** : `assets/wall_logos.webp` (versions pixel des logos officiels) et leur ordre dans `LOGOS`, en tête de `assets/walls.js`.

## Illustrations des articles

Les couvertures `assets/cover_*.webp` sont générées (pas de capture d'écran) dans la palette du site. Pour un nouveau billet, en générer une du même style (1200 × 800) ou laisser la vignette pixel se dessiner seule.

## Ajouter un billet

1. Dupliquer `blog/modele.html` en `blog/<slug>.html`, écrire le texte avec les composants qu'il montre, enlever la ligne `robots`.
2. Ajouter sa carte (`<li class="entry">`) en tête des deux listes de `blog/index.html`, FR et EN. Sans image, la vignette se dessine seule : `<canvas class="vignette" data-seed="<slug>"></canvas>`.
3. Pour qu'il apparaisse aussi sur l'accueil, ajouter la même carte dans la section `#articles` de `index.html`.
4. L'ajouter à `sitemap.xml`.

Un article interactif (comme `articles/sycophancy.html`) suit le même chemin ; ses widgets restent dans son propre `<style>`.

## Le hero

Tout est dans `assets/street.js` (chargé en bas de `index.html`, après `three.min.js` ; changer son `?v=` à chaque modification) : couches, événements (avion, étoiles filantes, chat, voiture, corbeau, fenêtre du codeur, arcade, enseigne), fréquences et amplitudes. Les fenêtres qui s'allument sont dans la constante `DOTS` ; les coordonnées sont en pixels de l'illustration (1456 × 816).

La cadence : 60 images par seconde au plus (un écran 120 Hz dessine une fois sur deux), et un appareil qui ne tient pas 45 images par seconde s'allège seul, une fois pour toutes (le reflet de l'eau recalculé une image sur deux, et sur un écran dense un canevas un peu moins grand où chaque pixel de l'illustration reste un nombre entier de pixels). Les murs des marges (`walls.js`) ne se reconstruisent que si la largeur de la marge ou la hauteur de la page change, et ne redessinent que les parties animées à l'écran.
