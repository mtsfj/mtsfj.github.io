# Playbook: how the street's best work was done

What the agents whose work the owner kept actually did, step by step, and the traps they fell into. Read it with
`tools/src/edits/FEEDBACK.md` (the owner's rules R1–R30 and his verdicts) and `tools/ARSENAL.md` (every tool, by place).
The helpers in `tools/dev/` are the ones used below.

## 1. Look first, at the whole street

- Render the whole street before touching anything (`node tools/dev/shot.cjs 22 out.png`, also 14 h, 3 h, `&night=red`),
  look at it at 1:1, then in x3 tiles. The owner's reproach when a part was judged alone: « prends du recul, tu vas voir tout
  seul ». A fix that is right in its box and wrong next to its neighbours is wrong.
- Name the problem the way he means it. Ask once when a word is ambiguous ("la grille", "l'écran", "à moitié visible"): a
  misread costs a whole round. When he circles something, copy his markup next to the work and look at it.

## 2. Geometry before pixels

- Build the place in 3D in the street's camera (`tools/interieur.py`, `tools/arcade_eave.py`: VP (700, 615), the eye at street
  level; each tool states its own focal), check every edge on its ray. A frontal wall's width is depth × focal / distance: a
  deep building's side runs out of the frame; never stop a wall where the picture runs out of things to draw.
- Ask what the camera can see: which corner can hide what (the roji's exit could only be half hidden by B's nearer corner, not
  the Centre's); what a window high up shows from below (only the ceiling); a strip between two fronts is the gable of one of
  them or a real gap, never a wall that belongs to no building.
- For a layout (a corner with machines, a room), draw the top view first, real sizes (a vending machine ≈ 1 × 0.82 × 2 m), no
  volume inside another; show it to the owner with the render.

## 3. Detail is generated, then brought into the painting (R28)

- Generate in context: crop the street around the place (at 22 h), describe precisely what to paint there, keep the painter's
  light; save the input, the prompt and the answer in `tools/src/edits/` (`<zone>_in.webp`, `_prompt.txt`, `_draft.webp`) so the
  tool rebuilds the same bytes. `openai/gpt-5.4-image-2` is the default (best here); `google/gemini-nano-banana-2.1` followed a
  layout guide better once. Several frames or variants per call, as one sheet.
- Bring it down to the painting: one scale (each scene pixel the mean of the pixels it covers, solid from half covered), the
  painting's tone families and grain (`tools/regrain.py`, `--families`), its night grade; no hard outline on the lit side; no
  flat colour block, no gradient without a light that explains it, no extra contrast.
- References: when a thing exists (the Black Ops perk machines and bottles, an anime's look), look it up online first and
  describe it faithfully; invent nothing (no made-up can). Never download or commit a third-party image.
- Budget: `GET https://openrouter.ai/api/v1/credits` before every call; stop under 1.5 $ (image output is refused under ~1 $)
  and ask the owner to top up. The key stays in `~/.config/openrouter/key`, never printed or committed.

## 4. Characters

- Regenerate whole sheets rather than repair a figure (Luffy's hat: a disc cut and slid read as a bug; a new sheet fixed it).
  The same identity in every frame; regenerate the one bad cell instead of patching it.
- Anchor frames on what doesn't move (the hips on a stool to the pixel; the planted foot in a walk), so only what should move
  moves; flick through every cell at x8.
- True scale (measure the metres per pixel at the figure's depth), no outline, painterly colour, graded as dark as what is
  round them, lit by the local lights (a lamp's warm rim, a screen's glow, the exit sign's green).
- Hidden is hidden: seen from behind, the bowl in front of him is not visible; a kickboard hides the stools' legs.
- A real person (the owner, his girlfriend): from a description only, never a photo sent or committed.

## 5. Light, states and the street's systems

- One painting, several states: a room painted once and relit (lit / lamp / screen / dark), never four different rooms.
- Lit windows are comps on their hours (`NHOURS`, `NSCHED`, `COMP_KIND`); two windows of one room light together.
- Every change follows the power cut (`PW`, the unlit layer `street_unlit.webp`), the red night (`NR*` masks and grades), the
  ground lights (`GL` table, `assets/gl_*.webp`), the wet ground and its mirror (`wet.webp`, `wet_mirror.webp`, written per zone
  from before copies), the drips (`DRIPS`: re-placed when an edge moves); a reflection takes the colour of what is above it.
- Uniform tone is measured, not eyeballed: plot the column profile across a face before/after (the giant screen's facade).

## 6. Life over time (R30)

- Everything new lives a little: `lightLife`, `stutOn`, the hours, gusts (`gust.k`); never in step with its neighbours; the
  power cut and the red night; still under reduced motion.
- Events are rare and choreographed (the Rocket grunt: out, furtive, lights up, Pikachu zaps him, he runs off down the roji).
- Cheap at runtime: sprite sheets loaded lazily, frames swapped at a few fps, drawn only when on screen and changing.

## 7. The pipeline

- Layers: zones in `tools/redraw_zones.py` (new zones appended at the END; a zone overlapping another takes that one's before
  copies and goes after it), patches in `tools/src/retouches/`, laid by `tools/bake_retouches.py`. Tools write from before
  copies, so they can be re-run and give the same bytes.
- After any change: `bash tools/dev/chain_twice.sh` until it prints SAME (after a merge the first run may still converge);
  `python3 tools/dev/changed_regions.py` to prove only the intended place changed; `?v=` bumped in `assets/street.js` (and
  `index.html` where listed) for every asset that changed; `python3 tools/poster.py` before going to main.
- Checks: `node tools/dev/smoke.cjs` (desktop and phone, 14 h, 22 h, 3 h, 5 h, red night; no page error, no 404). To force a
  state or step a clock for a capture, serve a hooked `street.js` (`tools/dev/hook.cjs`): nothing ships to visitors.

## 8. Showing the owner

- One line per item: what and why. Before/after at x3 and at 1:1, at 22 h and 14 h (3 h and the red night when relevant).
  Animations as MP4 (`bash tools/dev/to_mp4.sh x.gif`): his viewer doesn't play GIFs.
- Say honestly what is still weak. When it is a matter of taste, give 2–3 options rendered in the real street (branches or
  layer folders with `shot.cjs`), with a recommendation.
- Nothing goes to main without his explicit « Oui, pousse sur main ».

## 9. Merging several agents' work (the orchestrator)

- Each agent works in its own worktree from the branch tip, commits as Mathis Fajeau with a clean message (no mention of AI,
  no trailers), and doesn't push. Merge with `git cherry-pick -n`; on conflicts: versions bumped beyond both sides; re-apply the
  other side's `ASSETS` comps, `COMP_KIND` / `GL` / `DRIPS` entries; binaries (layers, retouches, `street.min.js`) taken from
  either side and rebuilt by the chain; then the chain until SAME, `changed_regions.py`, commit, push the branch.
- Tell the running agents when the tip moves, so they rebase before their final chain.

## 10. Traps already met

- `pkill` on browsers kills the other agents' captures: kill only your own processes.
- Shared temporary files race between agents (md5 lists, scratch renders): use your own temp dir.
- `git checkout --ours $(… | grep retouches)` once caught `tools/bake_retouches.py` and silently reverted a merge: name files
  exactly.
- A commit message with "image model" in it is refused by the owner's rule; hooks asking for another author are refused too.
- The session's scratch space can be wiped by a restart: helpers that matter live in `tools/dev/`.
- Several repeated screenshots in one page time out in headless software GL: one full screenshot per page load.
