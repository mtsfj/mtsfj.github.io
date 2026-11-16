#!/bin/bash
# The owner's viewer doesn't play GIFs: every animation preview is delivered as an MP4 too.
#     bash tools/dev/to_mp4.sh a.gif [b.gif ...]      (writes a.mp4 next to each: H.264, pixels kept sharp)
for g in "$@"; do
  ffmpeg -y -loglevel error -i "$g" -movflags faststart -pix_fmt yuv420p \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=neighbor" -c:v libx264 -crf 18 "${g%.gif}.mp4" && echo "${g%.gif}.mp4"
done
