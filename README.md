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
tools/fuji_aux.py        le masque exact du cerisier dans les calques du Fuji et le bord de sa pente (assets/fuji_aux.webp, boîte x 320..1016), pour l'aube
tools/tree_a.py          remplace l'arbre entre le magasin de boissons et l'oden (dessin : tools/src/tree_a.jpg)
tools/tree_bc.py         remplace le grand arbre devant la maison (dessin : tools/src/tree_bc.jpg), retire son buisson et redessine le pied du dojo
tools/left_tree_trim.py  abaisse l'arbre de gauche sous le toit de l'oden (sa propre cime peinte redescendue, par touffes entières) et prolonge le flanc du Fuji derrière lui
tools/cherry_gaps.py     voile les petits trous du cerisier (fuji_tree.webp) : le soir identique, plus de pois bleus le matin ni de taches la nuit
tools/night_far_clean.py nettoie night_far.webp (pixels de la rue mis à tort dans un plan lointain : lampadaire, bord du feuillage, barrière)
tools/dojo_window.py     le mur du haut au-dessus du dojo : tout en planches, et derrière l'arbre la fenêtre entière de la référence (tools/src/dojo_window_ref.png : son petit toit, son cadre, ses vitres, son garde-corps) posée sur les fuyantes du mur, son petit toit en volume et son ombre, sa lumière en sprite (assets/win_dojo.webp)
tools/kirua_house_side.py entre la maison du dojo et celle de Kirua : la descente commune et l'angle d'ombre du peintre remis ; la façade de Kirua dans sa propre perspective (son point de fuite, celui de sa gouttière et des planches du peintre), montée jusque sous la gouttière, les taches de l'ancien feuillage retirées ; son pignon visible, à plat, planches qui tournent l'angle
tools/kirua_gutter.py    la descente de la gouttière sous Kirua : boîte de collecte, col de cygne, tuyau contre l'angle, colliers, dauphin sur le toit bas, au métal de la gouttière dans chaque calque
tools/kirua_bay_window.py la façade de Kirua au-dessus du magasin de boissons : une grande baie vitrée à la place de la petite fenêtre, la pièce faite pour elle par le propriétaire (tools/src/kirua_bay_room.webp : voilage, bureau, lampe, écran, affiche, étagère) en petite boîte derrière l'ouverture, vue par l'œil de la rue (son image de face sur le mur du fond, assez grande pour couvrir la baie jusqu'à l'appui ; le plafond vu d'en dessous entre le haut de la baie et celui du mur, son spot et sa lueur ; le voilage sur le plan de la vitre, devant elle ; une ligne sombre au plafond contre le mur, le mur plus sombre dans l'angle et loin de la lampe), adoucie selon ses bords et ramenée à ses couleurs sans grain mais avec ses détails (le Fuji de l'affiche, l'écran et sa ville, les tiroirs du bureau, la lumière des spots en dégradés doux), ses lignes redessinées nettes ; la baie posée sur les fuyantes de la façade dans l'épaisseur du mur : chambranle (arêtes claires, dessous sombre), ébrasement (sous-face dans l'ombre, tableau à mi-ombre, bois du peintre avec son grain, occlusion dans les angles), ombre du linteau sur la vitre, appui en saillie et son ombre ; éteinte dans les calques (le verre sombre du peintre), sa lumière en sprite (assets/win_z7_up.webp, celui de la petite fenêtre) ; les planches du peintre refaites sous l'appui
tools/pole_cut.py        raccourcit le poteau de droite sous son transformateur (retiré) : chapeau de béton, collier, fût recopié du sien ; son occultation (COCC) depuis son sommet
tools/dojo_gap_pipe.py   la bande claire dans le passage entre le dojo et la boutique だがし décalée sous la descente commune : un seul tuyau d'aplomb de la gouttière au sol, l'arbre devant son milieu (ses pixels entre les feuilles et son pied sur le trottoir déplacés avec elle, le passage refait à sa place)
tools/tomare.py          止まれ sur la chaussée dans le bon ordre (止 au loin, れ au plus près) : chaque lettre portée par le sol dans la place de l'autre, dans layer_city_off, street_unlit et les lumières au sol gl_* (れ tirée de tools/src/tomare_re.png)
tools/zone5_facades.py   les trois maisons entre le cerisier de droite et le ramen : chacune son mur (carreaux, bardage, planches), un shoji, une porte en treillis, une plante, un vélo, une boîte aux lettres
tools/naruto_roof.py     retire l'étage au-dessus de la fenêtre de Naruto : la dalle du balcon devient le toit (acrotère et couvertine jusqu'au coin de C, le pilier du bout finissant avec eux ; côté proche au béton de la façade, un peu plus sombre, et bout de dalle), le mur latéral de la maison C que l'étage cachait (planches au grain de sa façade, coulures ; sa couvertine dans le prolongement de celle de sa façade, sur les mêmes rangs, une seule ligne qui tourne l'angle), à droite de la fenêtre sous la dalle la bande redessinée en aplats droits aux couleurs du peintre (dernier trumeau de la façade jusqu'à l'angle, descente d'eau du toit à l'angle avec ses colliers, mur du côté proche, planches d'angle de la maison voisine), et un jardin sur le toit vu d'en bas, au-dessus de l'acrotère sur rue : un érable du Japon en plateaux aux couleurs de l'arbre rouge du peintre, son tronc fourchu, des coussins d'arbustes taillés et une haie basse vers le coin proche (sources : tools/src/naruto_roof_leaves.png, les feuilles de l'arbre de gauche, pour le grain)
tools/roof_sway.py       le jardin du toit de Naruto dans le vent : rejoue tools/naruto_roof.py sur les calques d'avant lui et garde, dans sa boîte, ce que chaque plante couvre (le mur de C, le tronc, sinon le ciel) au soir et dans la coupure, quelle plante est chaque pixel, sa liberté (l'érable vers son sommet, le haut des arbustes et de la haie, la haie immobile sous le texte du menu) et où une feuille peut se montrer (assets/roof_sway.webp, lu par le bloc ROOF de street.js)
tools/e33_monolith.py    le Monolithe (Clair Obscur : Expedition 33), son sommet brisé, large, bas sur le flanc droit du Fuji, plan lointain à lui comme la tour (dessin : tools/src/e33_monolith_gold33.webp) ; écrit assets/e33_monolith.webp, e33_monolith_aux.webp (sa part dans l'air) et e33_mono33.webp (la lueur de son « 33 »)
tools/e33_banner.py      la bannière de l'Expédition au balcon de la maison du fond (dessin : tools/src/e33_banner_v2_33.webp) et la plaque près de sa porte ; la lanterne éclaire sa pointe (win_z9_lantern.webp) ; ce qu'elle couvre gardé dans tools/src/e33_banner_under.png
tools/e33_walkers.py     les passants du Gommage (assets/e33_walkers.webp et la description WKS dans street.js) : les deux planches du propriétaire (tools/src/e33_walker_sheet_24.webp, e33_walker_sheet_23.jpg) détourées, à la même échelle et sur la même ligne de sol, réduites sans grain ni bouillie, étalonnées au crépuscule du trottoir du fond ; la marche (les bottes reposées pour que le pied posé ne glisse pas), le demi-tour, le dos, la face ; l'ordre de leurs pixels dans le Gommage, le rouge de leurs pétales
tools/r6_sprites.py      les sprites du clin d'œil R6 : le drone (assets/r6_drone.webp, ses normales r6_drone_n.webp) et la petite caméra murale (r6_cam.webp), dessinés pixel par pixel d'après des modèles mesurés sur des vrais (un robot de reconnaissance lançable, un dôme de surveillance), et le boîtier de l'écran des caméras (r6_panel, r6_bezel, r6_key, r6_key_on, r6_ant .webp)
tools/dagashi_interior.py le dagashi-ya sous Kirua (remplace tools/dagashi_front.py) : par sa porte ouverte et la vitre de sa porte fermée, la boutique en petite maquette 3D vue par l'œil de la rue (la façade retrouvée d'après le seuil de la porte, à 6,33 m de l'œil ; le mur du bout de face à 27 m, le dessin du propriétaire posé dessus à l'échelle, tools/src/dagashi_room.webp : bocaux, boîtes, glacière à ramune, gacha, masques, jouets de papier, lampe ; le plancher surélevé, le comptoir à 25,7 m, le sol de planches, la caisse de ballons près de la porte, le tableau du poteau), chaque pixel pris sur 64 rayons et ramené à la couleur que portent le plus d'entre eux, à la lumière et à la palette de la boutique, au grain ; éteinte dans layer_city_off et street_unlit, allumée dans le comp assets/win_z7_shop.webp
tools/tabako_window.py   la fenêtre du tabac (mur de face) : une petite cabine derrière la vitre (le tableau du cadre, la paroi gauche, le fond poussé vers le point de fuite et coupé par le cadre droit, la lumière qui baisse vers le bas, un reflet) (assets/win_z7_kiosk.webp)
tools/interieur.py       (un module) une pièce vue par une ouverture d'une façade de côté : son fond de face (chaque rayon de la peinture redressé en horizontale, ses bords suivis, ses pixels gardés), le haut et le bas au grain de la peinture
tools/ichiraku_interior.py Ichiraku : derrière ses portes vitrées, la boutique en petite maquette 3D vue par l'œil de la rue (la façade retrouvée d'après le seuil des portes ; le mur du bout de face, le dessin du propriétaire posé dessus à l'échelle, tools/src/ichiraku_room.webp ; le comptoir à 1 m sur la ligne des figures, ses bols ; trois tabourets ; une lanterne), ramenée au pixel et à la palette de la boutique ; dans layer_city_off, street_unlit, shop_off.webp et le masque ramen_glass.webp
tools/ichiraku_figures.py Ichiraku : ses gens dans cette maquette, chacun à sa profondeur et à son échelle (Teuchi dans son allée, coupé par le comptoir et caché par ce qui est devant lui, à la porte avec sa perche jusqu'à la tringle du noren ; le client du coin et Naruto sur leurs tabourets, leurs bols devant eux ; le client qui va de son tabouret à la porte, une taille par pixel de hauteur, les pieds au sol) : des silhouettes nettes dans assets/ramen_figures.webp, leur place dans la ligne IRF de assets/street.js
tools/oden_window.py     la fenêtre de l'oden : la boutique de face derrière ses deux vitres, le plafond en coin au-dessus ; le comptoir et la marmite (d'où part la vapeur) à leur place
tools/red_sheet.py       les silhouettes de Red à la porte du balcon (assets/red_sil.webp), découpées de la planche du propriétaire (tools/src/red_sheet.webp) : une seule échelle, un seul sol, la marche de profil le pied posé immobile, l'arrêt, l'attente, le lancer (la Poké Ball ôtée, son vol dans ZRB), le demi-tour ; il remet à jour ZR, ZRC et ZRB dans street.js
tools/arcade_room.py     la salle d'arcade vue par sa porte : une petite maquette en 3D derrière l'ouverture (la porte retrouvée dans l'espace de la rue, la salle tournée de THETA, le mur du bout d'après le dessin du propriétaire, tools/src/arcade_wall.webp, à l'échelle d'une borne de 1,7 m, la machine à pinces et les bornes en boîtes, le sol de planches, le tube au plafond), projetée par la caméra de la rue, éclairée, réduite au pixel sans grain et mise à la nuit (assets/arcade_interior.webp, allumée et fermée ; la salle éteinte sous la porte dans street_unlit.webp ; ARC_PINS dans street.js)
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
