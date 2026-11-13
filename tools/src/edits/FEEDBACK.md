# The owner's verdicts on the street clean-up, and the rules they give

Each entry: what was shown, the owner's words, why it fell short (or worked), and the rule kept for the rest of the
street. Read this before redrawing any zone; add to it after every review.

## Rules

- **R1. Never add an object.** Redraw what is there, as what it is (the house's roof boxes are plant boxes, not air
  conditioners).
- **R2. The painter's light and palette stay.** Keep the zone's low frequencies (light falloff, glows, colour) from the
  painting; take only structure from a draft (`detail`), or bring a draft's colours back to the painting's (`hist`,
  `direct` with the fitted tint).
- **R3. Perspective is measured on the painting.** Street-parallel lines run to the vanishing point (700, 615); a circle
  on a receding face is an ellipse.
- **R4. Filtering is not enough.** Denoising and edge snapping change almost nothing visible: the defects are shapes
  that cannot be read, so the shapes are redrawn.
- **R5. A little depth, not much.** Flat boards, signs and wooden parts get a thickness, a lit edge and a shadow under
  them; no more.
- **R6. Painted smoke, steam and glow smears go.** The animations carry them; painted, they read as stains.
- **R7. Clutter that reads as noise goes.** A utility box that is only a smudge is removed (and anything animated from
  it), rather than detailed.
- **R8. The painter's silhouette is not sacred.** Keep an object's place, scale and anchor (a lantern's hook), not its
  outline, when the redraw is better.
- **R9. A surface is cleaned whole.** To its natural edges (the pavement, the corners), never half a wall: a clean top
  over a grainy bottom shows the seam.
- **R10. What is laid on a zone is redone with it.** Before changing a zone, list what street.js draws over it (comps,
  sprites, the closed shop's overlay, glass masks, neon glows) and keep them fitting.
- **R11. Whatever hangs or stands keeps what holds it.** A lantern needs its bracket or the eave above it; a "stray"
  lit dash next to an object may be its fixing: look at what it touches before removing it.
- **R12. Depth comes from light and shading, not outlines.** A round thing is darker at its turning edges; a lit thing
  lights the wall behind it (a soft pool). A halo hugging the outline reads as a sticker.
- **R13. A redraw holds in every state.** A place that shuts (the dojo, the oden, Ichiraku) shows the unlit layer: give
  it the new picture darkened as the painter darkened his, channel by channel (the night's blue, not a dim orange).
- **R14. When an object keeps failing, change the object.** After two redraws the paper lanterns still did not work;
  plain wall lamps (an iron arm, a glass shade, their light on the wall) did. Prefer the simpler fixture.
- **R15. A pair on one wall is one way round.** Two lamps on the same wall share their orientation (not mirrored) and
  their height follows the wall's perspective line.
- **R16. Show options in the real street, from real references.** When a choice is open, put three or four options in
  the street at once (the owner picks in seconds), each grounded in what real places look like.
- **R17. Check the draft object by object before integrating it.** A draft that drops, merges or swaps an object (a
  glazed side door turned into more shutter, a slatted door into a western panel door, a sign's text wiped) is rejected,
  not patched: no polygon or method brings back what the draft lost.
- **R18. Blotches set the low-pass.** The painter's light is kept below a scale (`sigma`); it must be wider than the
  noise it hides (Ichiraku's grain: 6; the oden's five-pixel blotches: 10) and narrower than the light's falloff.
- **R20. Keep objects by their shape, not a box.** A box kept around a lantern or a lamp keeps the old wall inside it:
  a square of grain on the clean wall. Keep the object's own pixels (its lit paper and its outline), clean the wall up
  to it, leave the object out of the light taken from the painting and out of the drawing's detail (else it rings dark
  around it), and fade a part's edge into the old painting over a few pixels.
- **R21. A draft may slide what is next to an ambiguous edge.** Crop the draft's input away from what it cannot read
  (a pole in front, a neighbour's sign), check the draft's columns against the painting's, and register over a wider
  reach with the edges held (never wrapped round) when it moved the whole.
- **R22. What is behind a foreground object goes on behind it.** Next to a pole, a sign or a tree in front, an object
  is cut by its edge and continues out of sight; it is never shrunk to fit the part that shows (the owner: "tu as voulu
  tout faire rentrer alors qu'une partie est cachée derrière le poteau, ce qui donne cette impression de comprimé").
- **R23. Follow the neighbours' drawing, and fix perspective at the outline.** Where the painter drew a stretch face on
  (the menu board and Ichiraku's frames by the pink door), a redrawn object there stays face on: warped alone onto the
  vanishing point, it seems to sink into the wall. What must follow the street's lines is its outline: its step on the
  sidewalk's slope, its meeting with the next facade. A recess in a facade on the right shows its left side (toward the
  vanishing point), never its right one: there the frame meets the facade with a shadow line, not a pillar.
- **R24. Behind what stands in front, draw the whole at once, then lay it back.** Next to a pole, a sign or a tree in
  front, the strips on either side are not redrawn apart (each squeezes its own logic into too little room: a "garage"
  in ten pixels): the draft is asked of the street with the object taken out, the walls run on behind it as one front,
  and the object is laid back over them as painted (its trace, its edge pixel blended again with the new background).
  The owner: "fais un truc global derrière le poteau et après tu repasses le poteau devant : au moins t'as pas à
  réfléchir à la logique physique et au POV".
- **R25. A plain building stays simple and logical.** One building, one material from its roof to the sidewalk, and a
  few large openings that say what it is (a garage, a shop window with its room behind); small accessories drawn at this
  size (a thin side door, a sign band, a shutter box, a bucket, an intercom) read as clutter. The owner: "pas cohérent,
  porte trop fine, trop de trucs inutiles ; fais simple et logique : mur uni, grand garage, baie vitrée + intérieur",
  then "unifier sa texture sur tout le bâtiment".
- **R19. Whatever copies the wall follows it.** Swinging, sliding or blinking overlays often carry a copy of the wall
  behind them (the oden's lantern frames, its door's sliding leaf); they take the new wall too, or they show the old
  one each time they move.

## Verdicts

| Date | Shown | Owner | Why | Rule |
| --- | --- | --- | --- | --- |
| 2026-11-10 | First pass: 73 items rebuilt as 3D mock-ups | Only the drinks machines kept: "inventions, style, plat, mauvaise perspective" | Objects made up, smooth fills, circles instead of ellipses, retinted zones | R1, R2, R3 |
| 2026-11-12 | "Clean only" pilot (speckle removal, edge snapping) | Not worth it | Invisible: the problem is unreadable shapes | R4 |
| 2026-11-12 | Ichiraku sign, two designs | B kept: lacquered board seen from below, emblem, neon tubes | The old sign: blurry text, no depth | R5 |
| 2026-11-12 | Painted steam on Ichiraku's wall | "ce truc là moche" | A static smear over the animated steam | R6 |
| 2026-11-12 | Ichiraku's vent box, cleaned | "virer la bouche d'aération qui fait de la buée" | A box that adds nothing | R7 |
| 2026-11-12 | Ichiraku's door | "la partie bois doit ressortir un peu en 3D" | The eave was flat | R5 |
| 2026-11-12 | Lanterns redrawn slender, as painted | "elle était bien [la ronde]... pas obligé de fine ni ronde" | I held to the old outline | R8 |
| 2026-11-12 | Ichiraku's wall cleaned to y 560 | "le bas du mur a full grain alors que le haut non, faut uniformiser" | Only my polygon was cleaned | R9 |
| 2026-11-12 | Rooftop fan, sign B, clean plaster, wooden eave, round lanterns | Kept ("c'est ce style de détail que je veux") | Legible shapes, the painter's light, a little depth | R2, R5 |
| 2026-11-12 | Round lanterns | "pb de calque, lanterne derrière la façade ; les lanternes font vraiment aplat 2D" | I had removed their brackets (taken for stray dashes), so they floated; flat fill, a halo hugging the outline | R11, R12 |
| 2026-11-12 | Round lanterns with brackets, shading and a light pool | "les lanternes d'Ichiraku trop moches, remplace par une light normale" | A paper lantern drawn small never read well here | R14 |
| 2026-11-12 | Five light options in the street (red barrel, square andon, white chōchin, red ball, wall lamps) | The wall lamps, "à paralléliser" (not mirrored: one wall) | The lanterns never sat well at this size; mirrored arms read as two walls | R14, R15, R16 |
| 2026-11-12 | Four options over the door (wooden eave, steel vent hood, tiled roof, lit lattice transom) | V3, the lattice transom without an awning | The simplest, lit from inside like the shop | R16 |
| 2026-11-12 | (my own review) Closed shops by the pole, cleaned from a draft | Not shown: the draft had turned the glazed side door into shutter, the slatted door into a panel door, wiped the sign | The draft changed what the objects are | R17 |
| 2026-11-12 | Oden front: walls in dark planks, crisp noren, clean eave and door wood, open and shut | "vraiment pas clean sur les transitions entre façade et texture, trop abrupt, carré" | The lantern and the lamps kept in boxes of old grain; the eave cut straight under the roof | R20 |
| 2026-11-12 | The oden's box by the window ("les boîtes aux lettres en bas, c'est quoi ?") | "peu importe" (remove it or redraw it) | A 12 x 36 px box nobody can read: two stacked capsule machines, or a menu? Removed with the red dots by it: the planks down to the wall's foot (y 660, not the box's), the pavement it stood on continued from beside | R7 |
| 2026-11-12 | Ichiraku's noren cleaned; the oden front with its transitions softened and the box removed, seen on the whole site (desktop, phone) | "ok", "good": on main (ed7d038) | Shapes that read, no seams, the painter's light | R17-R20 |
| 2026-11-12 | Tobacco kiosk: its lit cabin (packs, notice, coin tray) legible, the same dim behind shut glass, its plates and planks cleaned | (awaiting) | Packs were an orange smear; a shut window's detail kept as soft as the painter's (shut_k) | R13, R17 |
| 2026-11-12 | (draft) the Pokemon Center's ball sign, a first draft with a dark outline | "évite les contours : si c'est une sphère, il y a de l'ombre sur le côté, pas de contour" | An outline makes a sticker; a sphere turns into shadow at its edge | R12 |
| 2026-11-12 | Pokemon Center's ball sign redrawn as a sphere, no outline: shaded to its edge, red and white fitted apart, the button glowing as the painter's | (awaiting) | A fit over the whole ball pinked its white; the painter's light (detail) brought the outline back; the drawing's sphere plus the painter's glow kept both | R12 |
| 2026-11-12 | Tobacco kiosk's planks above the sign, cleaned to the roof (the wall whole, R9); the neighbour's lines left whole | (awaiting) | A zone's edge across a thin line cuts it: keep the edge off lines that run on | R9 |
| 2026-11-12 | The pink-lit doorway by the pole: awning, arched transom, sidelight, paneled door, plaque and slot cleaned | (awaiting) | The first draft turned the pole's sign into slats and slid the door 5 px: cropped right of the pole, registered 4 px | R17, R21 |
| 2026-11-12 | Tobacco kiosk's lit cabin redrawn (packs crisper) | "bizarre la caisse du soda shop, je comprends pas ce qui a changé, je préfère l'ancien ; essaie d'autres variantes" | A change too faint to read reads as a mistake: either clearly better or left as painted | R16 |
| 2026-11-12 | (my own review) The closed shops by the pole, second try: a draft told to keep every object | Not shown: faithful, but it changes almost nothing visible (the zone is cleaner than it looked) | A change nobody can see is not worth a commit (the kiosk's lesson) | R4, R16 |
| 2026-11-12 | Pink doorway: its right side | "tout le côté droit de la porte est bizarre" | The painter's jagged black edge just outside the zone, next to a clean door, read as a tear: made an even strip in shadow | R9 |
| 2026-11-12 | The pink strip left of the pole, option B: a tall lit signboard drawn by the draft | "wtf, c'est face à nous, aucune perspective, tout est faux" | Drawn face on, on a wall that recedes to the vanishing point; far too bright. Never show a draft's object before checking it is foreshortened like its wall | R3 |
| 2026-11-12 | (same) | "tu as voulu tout faire rentrer alors qu'une partie est cachée derrière le poteau : impression de comprimé" | The whole sign squeezed into the visible strip instead of running on behind the pole | R22 |
| 2026-11-12 | Pink door: lit warm or pink, warped onto the vanishing point | "aucune, wtf la perspective, elle s'enfonce ; prends le temps, utilise les outils des anciens agents" | Warped alone while its neighbours are drawn face on; the real faults were at its outline (a false pillar by Ichiraku, a level step) | R23 |
| 2026-11-12 | Kiosk window options | B, the Showa showcase counter | | R16 |
| 2026-11-12 | Pink strip left of the pole: plain wall, or a sign in perspective cut by the pole | "aucune des deux, c'est désastreux" | Kept as painted | R6, R22 |
| 2026-11-12 | Pink door corrected: face on like its neighbours, Ichiraku's wall up to its frame, its step on the sidewalk's slope, pink or warm | "toujours désastreux" | Three passes on it made it worse: put back exactly as painted. A spot that resists twice is left as painted unless a clearly better way is found (R14) | R14 |
| 2026-11-13 | (the owner on the site) the Pokemon Center's ball "with a black rim" | "my bad, mon site était pas à jour" | His browser's copy was old: no change | |
| 2026-11-13 | (draft, in my scratch) the house's door right of the pole, a Japanese entrance this time (the old draft had drawn an English door with a fanlight: a style the street has nowhere) | "ce morceau de garage entre la porte et le poteau n'a pas de sens, pas assez d'espace ; fais un truc global derrière le poteau" | Ten pixels of wall between the pole and the frame, drawn on their own, read as a shutter | R24 |
| 2026-11-13 | (draft) the ground floors redrawn whole with the pole taken out | "vire le truc ; améliore le rapport des deux ; vire cette bouillie IA" | A post at the awning's end under Ichiraku's sign, gone (the awning continued along its ray); the hall's lamp, intercom and panels, mush at this size, gone (its lit wall alone); the two buildings' corner lies wholly behind the pole once it is back | R7, R24 |
| 2026-11-13 | (same) | "moche : trottoir à côté d'Ichiraku" | A speckled band under Ichiraku's cleaned plaster, beside the new step: the plaster carried down to the facades' foot line (as the step), the sidewalk continued under it | R9, R23 |
| 2026-11-13 | Both entrances by the pole, the pole laid back, in every state | "mieux porte" | The house's entrance reads; the building left of the pole now stood out | R24 |
| 2026-11-13 | (the owner on the site) the apartment building's ground floor left of the pole | "pour moi ce rdc est à refaire complet" | The shop front was a dark void over a shutter, a sign band of mush, a door specked with pink | R4 |
| 2026-11-13 | (draft, in my scratch) its shop shut: shutter, its box, a sign band, a thin side door, the bucket | "non, pas cohérent, porte trop fine, trop de trucs inutiles ; fais simple et logique : mur uni, grand garage, baie vitrée + intérieur" | Each accessory faithful, the whole cluttered | R25 |
| 2026-11-13 | Two options in the street: a plain wall with a big garage shutter, or with a shop window and its lit room | "le plus beau c'est la fenêtre ; vire l'interrupteur (dans le hall) ; unifier sa texture sur tout le bâtiment" | The shop window kept; the eleventh's switch box (it stood on the old pier, now plain wall by the window) moved onto the hall's wall, lit by the hall; the building's weatherboards (zone5) made plaster like its ground floor, from roof to sidewalk, its two lit windows' overlays with it | R16, R25 |
| 2026-11-13 | The building in plaster, the shop window, the switch box in the hall | "pas la même teinte ; vire les petites fenêtres à droite des grosses ; pas de contour à l'interrupteur, ça tue le contraste, on l'a pas" | The ground floor's wall (the draft's, teal) brought to the plaster's violet over the ledge, channel by channel; the two narrow windows filled with the plaster (the violet one's lit overlay and ground light removed); the box drawn without its black outline, its edges its own light | R12, R25 |
| 2026-11-13 | Three agents' survey of the street (left, middle, right), the worst checked by eye | The owner chose: Ichiraku's foot and door bottoms, the drinks machines' pool, the dojo's foot and the dark gap | Seams where a cleaned zone ended (a straight cut over old grain), an overlay drawn dithered, a flat black hole | R9, R20 |
| 2026-11-13 | (done) The machines' light on the sidewalk a soft pool (its footprint smoothed, the pavement's relief under it, its light in total kept); the dojo's kick panels down to a threshold on its ray, its post plain, the gap a navy passage (its olive slab gone); Ichiraku's door bottoms clean boards in the painter's light, the plaster right of them down to the sidewalk | (awaiting) | | R9, R13 |
| 2026-11-13 | (done) The house at the street's end (tools/end_house.py): its paper lantern, off a flat red disc, now a barrel with lacquered caps, darker turning sides and its iron bracket to the door's jamb, the same lit (the comp) and off (darkened channel by channel as the painter darkened his); its upstairs window a pair of curtains (the painter's left one cleaned, mirrored on the right where dark blocks were), lit and behind the dark glass; its railing's bars every 9.5 px between its posts, the middle one on the meeting stiles, in both states | (awaiting) | | R11, R12, R13 |
