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
