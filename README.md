# mtsfj.github.io · site perso

Site statique, aucun build : ouvrir `index.html` suffit.

```
index.html              accueil (hero three.js + bio + articles + publications + contact), FR/EN
blog/index.html         le blog : tous les billets et articles, en cartes (FR/EN)
blog/modele.html        le modèle d'un billet (non référencé) : tous les composants de texte
articles/pinductor.html walkthrough interactif du papier Pinductor (EN)
articles/sycophancy.html article interactif du projet sycophancie (EN)
assets/site.css         la charte graphique : couleurs, polices, composants (partagée par toutes les pages)
assets/site.js          langue FR/EN, e-mail révélé au clic, BibTeX, vignettes pixel générées
assets/                 couches de l'illustration (WebP) et sprites
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

## Langue

`?lang=fr` ou `?lang=en` dans l'URL force la langue ; sinon celle du navigateur (français uniquement pour un navigateur en français).

## La charte graphique

Toutes les pages chargent `assets/fonts/fonts.css`, puis `assets/site.css`, et `assets/site.js` en fin de page. Le `<style>` d'une page ne garde que ce qui lui est propre (la rue de l'accueil, les widgets d'un article).

- **Couleurs** : la rue la nuit. `--night` (fond), `--night-deep` (barre, haut de page), `--panel` (surfaces), `--paper` / `--paper-dim` (texte), `--pink` (néons : titres, étiquettes), `--sodium` (lampadaire : dates, chiffres, action principale). Cyan, vert et violet : données seulement.
- **Polices** : Silkscreen (pixel) pour les titres de page et les petites étiquettes, jamais pour du texte courant ; Inter Tight pour tout le reste ; JetBrains Mono pour le code.
- **Composants** : `.site-bar` (barre du haut), `.masthead` + `.eyebrow` + `.display` + `.lede` (en-tête de page), `.section` + `.section-head` (numéro, titre pixel, filet néon) (sections), `.split` (texte + panneau à droite), `.lead` (premier paragraphe), `.projects` / `.project` (cartes de projet), `.cta` (appel à l'action), `.skyline` (la ligne d'immeubles du bas de page), `.fig` + `.game` (FIG. 01 : quatre agents autotéliques qui se disputent une grille, chacun choisissant ses buts par progrès d'apprentissage), `.wall` (sur grand écran, les marges deviennent les façades de la rue : fenêtres, néons, lanternes, distributeurs, escaliers… générés par `site.js`), `.metric` + `.bars-mini` (le chiffre d'un projet), `.entry-media.cover` (illustration d'un billet), `.entry` (la carte d'un billet : vignette, méta, titre, phrase, liens) dans `.entries` ou `.entries-grid`, `.badge`, `.chip`, `.btn`, `.links`, `.rows`, `.kv`, `.dated`, `.chrono` (frise), `.tile`, `.panel`, `.prose` (texte long), `.takeaway` (encadré), `.site-footer`. Chacun est décrit en une ligne dans `site.css`.

## Illustrations des articles

Les couvertures `assets/cover_*.webp` sont générées (pas de capture d'écran) dans la palette du site. Pour un nouveau billet, en générer une du même style (1200 × 800) ou laisser la vignette pixel se dessiner seule.

## Ajouter un billet

1. Dupliquer `blog/modele.html` en `blog/<slug>.html`, écrire le texte avec les composants qu'il montre, enlever la ligne `robots`.
2. Ajouter sa carte (`<li class="entry">`) en tête des deux listes de `blog/index.html`, FR et EN. Sans image, la vignette se dessine seule : `<canvas class="vignette" data-seed="<slug>"></canvas>`.
3. Pour qu'il apparaisse aussi sur l'accueil, ajouter la même carte dans la section `#articles` de `index.html`.
4. L'ajouter à `sitemap.xml`.

Un article interactif (comme `articles/sycophancy.html`) suit le même chemin ; ses widgets restent dans son propre `<style>`.

## Le hero

Tout est dans le `<script>` en bas de `index.html` : couches, événements (avion, étoiles filantes, chat, voiture, corbeau, fenêtre du codeur, arcade, enseigne), fréquences et amplitudes. Les fenêtres qui s'allument sont dans la constante `DOTS` ; les coordonnées sont en pixels de l'illustration (1456 × 816).
