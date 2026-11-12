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
