# Mémo : toutes les demandes (site mtsfj.github.io)

Règles générales, à respecter partout
- Rien ne doit dégrader la qualité : seulement l'augmenter. Intégration « seamless ».
- Montrer les résultats avant de mettre en ligne quand c'est une nouveauté visible (pour les réparations et l'invisible : feu vert donné, « je te laisse tout gérer »).
- Scène : plus un seul pixel de défaut à la fin. Tout naturel, seamless, à tout zoom, sous tout filtre et tout dégradé.
- Pour la scène : ne pas rajouter de choses, réparer, avec la version nuit comme modèle (sauf demande explicite comme l'animation du matin).
- Ne pas s'arrêter tant qu'il reste un défaut.

## Fait
- [x] Performances (murs, cadence 60 i/s, script à part, WebP sans perte, cache navigateur) — en ligne.
- [x] Matin après le secret : trait lumineux à travers le cerisier, moucheté près de la Pokéball, faux feuillages bleus, Fuji éclairé à 100 % jusqu'au cerisier, liseré blanc des pentes.
- [x] Matin : lampadaire (bleu ciel + trait rouge), faux trous bleu ciel au coin du bâtiment (masque night_far).
- [x] Matin : porte du bâtiment central (tache bleue, lueur), bandes orange du ramen fermé.
- [x] Matin : ville du fond (panneau rouge saturé, trait magenta de la barrière, lumières qui suivent la coupure).
- [x] Corniche derrière l'arbre de gauche retirée (nuit et générale).
- [x] Trouées dans l'arbre de gauche (ciel, pagode, pied du Fuji prolongé), sans morceau flottant.
- [x] Référencement : rel="me", sitemap, IndexNow (Bing…). Les liens de profil sont déjà sur le site / le CV.

## À faire
- [x] Cerisier de droite, matin : liseré violet retiré sur toute sa largeur, pixels couleur roche → roche, poches de roche dans le feuillage → ton d'ombre de nuit (en ligne e42a64f).
- [x] Trouées de l'arbre de gauche : réparties sur le haut de l'arbre (le bas cache le toit de l'oden, non peint dessous : pas de trouée possible sans repeindre).
- [x] Pétales et secousse du cerisier étalonnés selon le mode (en ligne e42a64f). Pétales de la gouttière : prennent déjà la lumière de la scène.
- [x] Animer le matin comme la nuit : après le secret, le courant revient par vague puis les boutiques ouvrent une à une sous le ciel du matin (en ligne f9779cb).
- [x] Search Console : session « Search Console : mtsfj.github.io (guide) » lancée (session_01VfuX6DnbZ5ryfEn1b1PHRo), l'utilisateur lui parle quand il veut.
- [x] Chasse aux défauts restants dans tous les états : soir, nuit profonde, nuit rouge, coupure de courant, aube (Fuji rouge, doré), matin ; tout zoom. Trouvés et corrigés en route : trait sombre dans la brume (îlot night_far), taches rouge sombre de la ville du fond au matin d'un visiteur (7 h 30).
- [x] Le matin a les mêmes défauts que l'ancien matin après secret sur la ville du fond : lumières de la ville du fond (fenêtres et enseignes) qui s'effacent dans l'air du matin, flaques de lumière des boutiques au sol à moitié noyées par le jour.
- [x] Trous du cerisier de droite (pois bleus le matin, taches sombres la nuit) : voilés, le soir identique (tools/cherry_gaps.py).
- [x] Vérifier toutes les heures et tous les modes avant de pousser ; accessibilité téléphone (cibles tactiles ≥ 24 px, zones défilantes au clavier, aucun débordement, axe WCAG 2.2 AA sans erreur).
- [x] Raccourcir l'arbre de gauche pour qu'il ne dépasse pas des bâtiments (égal ou un peu en dessous), pour aérer : cime au niveau du toit de l'oden (y 448-457), flanc du Fuji prolongé derrière.
- [x] Coupe de l'arbre de gauche moins droite, réaliste : sa propre cime peinte redescendue par touffes entières (sommet 450 = toit de l'oden), qui passe derrière le toit bas près du mur ; flanc droit abaissé de 8 px. Au passage : bande sombre sous l'avant-toit de la maison retirée (reste de l'arbre).
- [x] Alléger la brume du matin sur la ville du fond (oui, en ligne 8adb575) : voile de jour 45 % → 25 %, nappe d'horizon moitié moins dense le matin.
