# Passation : remplacer les arbres A et B+C par des arbres générés (FLUX Fill)

À lire par la session suivante. Ce dossier `handoff/` n'existe que sur la branche de travail : **ne jamais le pousser sur main**
(le retirer avant tout `git push origin HEAD:main`). Le mémo complet des demandes est dans `MEMO_demandes.md`.

## Règles de l'utilisateur (Mathis, écrit en français familier, souvent sur téléphone)
- Plus un seul pixel de défaut : naturel, seamless, à tout zoom, toutes heures, tous modes de calque.
- Ne rien dégrader. Montrer un avant/après avant de mettre en ligne une nouveauté visible ; réparations : il laisse tout gérer.
- Pousser sur main seulement une fois sûr sur toutes les heures et modes + vérif téléphone.
- Pousser : `git pull -q --rebase origin main`, puis la branche, puis `git push origin HEAD:main`. Commits en français + trailers.

## Ce qui est en ligne (8adb575)
- Arbre de gauche (A) : cime refaite à partir de sa propre cime peinte (`tools/left_tree_trim.py`, depuis aa383bc), sommet à 450
  (toit de l'oden), flanc du Fuji prolongé derrière (x < 378, night_far = 160). Bande sombre sous l'avant-toit retirée.
- Brume du matin allégée (dwFar 0.45 → 0.25, `SKYF.air` sur fogs[0]).

## La demande en cours
« Tout retirer, générer un vrai arbre, juste le faire dépasser de ce qu'il faut ; pareil pour le devant du dojo. Si ça ne couvre
pas, interpoler (texture). » Zones (voir `zones.png`) :
- **A** : l'arbre de gauche, x 326..491, entre le mur de la maison (x 325) et l'oden ; cime ≤ 450 ; le toit bas devant lui
  (bord y = 454 + 1.22 (x - 326)) et le toit bleu de l'oden restent devant / intacts.
- **B+C (un seul arbre)** : le grand arbre sombre de premier plan à gauche (x 0..232, y 30..480) et son buisson devant le dojo
  空手道場 (x 0..115, y 590..785). Derrière : mur en planches de la maison, bas d'une fenêtre (haut gauche), jonction des toits
  au-dessus de l'enseigne du dojo, shoji éclairés du dojo.

## Méthode prévue
1. Token : `HF_TOKEN` (variable d'environnement) ; `pip install gradio_client`. Espaces : `black-forest-labs/FLUX.1-Fill-dev`
   (`/infer`, edit_images = {background, layers:[masque], composite}, prompt, width/height, guidance ~30-50, steps 28) pour peindre
   dans la scène ; `FLUX.1-schnell` / `FLUX.1-dev` pour des essais isolés. Quota ZeroGPU limité par jour.
2. Base : `scene_soir_1456x816.png` (soir peint, sans interface ; refaite par `dev/clean_scene.js`). Recadrer autour de la zone,
   agrandir ×3-4 (plus proche voisin), masque = ancienne végétation + place de la nouvelle cime, générer plusieurs graines, réduire
   (moyenne par zone) à la taille de la scène, ne garder que l'intérieur du masque.
3. Séparer l'arbre de l'arrière-plan généré : derrière A, le ciel/Fuji viennent de leurs propres calques (laisser transparent dans
   layer_city_off au-dessus du flanc ; à gauche de x 378, le flanc prolongé est peint dans le calque de rue, night_far = 160) ;
   les façades reconstruites (oden, mur, dojo) vont dans le calque de rue.
4. Écrire dans **tous** les calques : layer_city_off (soir), street_unlit (coupure / boutiques fermées : dériver du rapport
   unlit/lit de l'ancien arbre et des surfaces voisines), night_far (0 = rue), street_sun (0 sur l'arbre ; surfaces éclairées par
   le soleil bas : reprendre les voisines), puis `python3 tools/fuji_aux.py`. Penser aux lumières du dojo (zone des heures 9,
   `gl_dojo.webp`, shoji peints dans la rue) et au reflet au sol si l'arbre y touche.
5. Montées de version : `?v=` dans `assets/street.js` (layer_city_off, street_unlit, night_far, street_sun, fuji_aux) et dans
   `index.html` (préchargement layer_city_off, street.js).

## Vérification (scripts dans `dev/`, chemins à adapter au scratchpad de la session)
- Serveur : `(setsid nohup python3 -m http.server 8123 &)` à la racine du dépôt.
- `python3 dev/mkdbg.py` (depuis la racine) crée `_dbg.html` / `_dbg_street.js` (à supprimer avant commit).
- `H=1 node dev/seq2.js <prefixe> 19.5,1,5.75,6.4,7,7.5` (heures) ; `node dev/modes.js <prefixe>` (nuit rouge, coupure) ;
  `node dev/seq2.js <prefixe> 8,14,30` (aube finale après le secret). Chromium = SwiftShader : lent, quelques minutes par image.
- `node dev/chk.js` (pages sans erreur), `node dev/phone.js <prefixe>` (téléphone 390×844 : débordement, erreurs).
- `dev/dusk_comp.py` : composite rapide du soir peint depuis les calques (sans rendu), pour itérer.
