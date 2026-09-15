# mathis-fajeau.github.io — site perso

Site statique, aucun build : ouvrir `index.html` suffit.

```
index.html              accueil (hero three.js + bio + articles + publications + contact), FR/EN
articles/pinductor.html walkthrough interactif du papier Pinductor (EN)
articles/sycophancy.html article interactif du projet sycophancie (FR/EN)
assets/                 couches de l'illustration (WebP) et sprites
cv.pdf                  CV
favicon.png, og.png     icône et image de partage
```

## Déployer sur GitHub Pages (gratuit)

1. Créer un repo public nommé `ZWhimsi.github.io` (ou n'importe quel nom, l'URL sera alors `zwhimsi.github.io/<nom>`).
2. Copier tout ce dossier à la racine du repo, `git push`.
3. Settings → Pages → Source : « Deploy from a branch », branche `main`, dossier `/ (root)`. En ligne en une minute.

Le fichier `.nojekyll` évite que GitHub ignore certains fichiers.

## Déployer sur Vercel / Netlify

Importer le repo, framework « Other », aucune commande de build, dossier de sortie `.`.

## Domaine perso (optionnel)

Un `.fr`/`.com` à ~10 €/an chez n'importe quel registrar, puis Settings → Pages → Custom domain (GitHub) ou Domains (Vercel). HTTPS automatique.

## Langue

`?lang=fr` ou `?lang=en` dans l'URL force la langue ; sinon celle du navigateur (français uniquement pour un navigateur en français).

## Ajouter un article

Dupliquer `articles/sycophancy.html` (les styles sont dans le fichier), écrire le contenu, puis ajouter l'entrée dans les deux listes (FR et EN) de la section `#articles` de `index.html`.

## Le hero

Tout est dans le `<script>` en bas de `index.html` : couches, événements (avion, étoiles filantes, chat, voiture, corbeau, fenêtre du codeur, arcade, enseigne), fréquences et amplitudes. Les fenêtres qui s'allument sont dans la constante `DOTS` ; les coordonnées sont en pixels de l'illustration (1456 × 816).
