# aOS teaser

Short films for aOS, the AllisonOS app store. Each plays on its own in a browser; a tap pauses it.

- `index.html`: the 45-second teaser, "Break free · Coming soon".
  https://tomallison24.github.io/aos-teaser/
- `launch/index.html`: the 30-second launch-eve teaser. aOS launches tomorrow (10/10/26), the core apps,
  and "Your invite to aOS arrives in the next 24 hours". A ready-to-send video of it is
  `launch/aos-launch-teaser.mp4` (1080x1920, 30fps), with a soft original score timed to the film.
  https://tomallison24.github.io/aos-teaser/launch/
  The page plays the same score (`launch/music.mp3`, made by `make-video/music.py`): it opens on a
  "Play with sound" button, since phones only allow sound after a tap, and the film follows the music's clock.

To remake the MP4 (`launch/make-video/`): serve the repo (`python3 -m http.server 8765`), run
`node render.mjs film.mp4` (Playwright), `python3 music.py music.wav` (numpy), then
`ffmpeg -i film.mp4 -i music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest aos-launch-teaser.mp4`.

- `aos2/index.html`: the aOS 2 teaser, "Every app, one home", 38 seconds in the Vintage design (cream,
  mustard, teal, burnt orange and walnut; Futura, or Jost where there's no Futura: `fonts/Jost.woff2`).
  Fourteen apps, each alone, then fourteen homes; they gather into one, and aOS's Home opens on a phone:
  Weather slides in with "‹ aOS" in its corner and swipes back. Then Ipsy, asked across the apps, the design
  flipping from Vintage to Sea glass, the mark with its 2 dropping in, and "Open aOS to see it". A ready-to-send
  video is `aos2/aos2-teaser.mp4` (1080x1920, 30fps), with its own soft score (`aos2/music.mp3`, made by
  `aos2/make-video/music.py`, in F this time); the page opens on "Play with sound" like launch/. The icons are
  the apps' Vintage ones (`aos2/icons/`).
  https://tomallison24.github.io/aos-teaser/aos2/
  To remake it (`aos2/make-video/`): the same steps as launch/, with `node render.mjs film.mp4` and
  `node render.mjs --og og.png` for the link preview (`PORT=` if the server isn't on 8765).

- `welcome/`: launch day. A joke (take the "ch" out of chaos: aOS), then "Your wait is over" and the
  welcome to the aOS family. `welcome/#name=Sarah&invite=CODE` greets them by name and its button opens
  their own aOS invite; `welcome/#make` turns a name and an aOS invite link into that welcome link.
  Everything after the # stays in the browser.
  https://tomallison24.github.io/aos-teaser/welcome/

Published with GitHub Pages. Add `?export` to any of the films to drive it frame by frame (`window.renderAt(t)`).
