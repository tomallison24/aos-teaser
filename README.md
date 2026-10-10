# aOS teaser

Two short films for aOS, the AllisonOS app store. Each plays on its own in a browser; a tap pauses it.

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

- `welcome/`: launch day. A joke (take the "ch" out of chaos: aOS), then "Your wait is over" and the
  welcome to the aOS family. `welcome/#name=Sarah&invite=CODE` greets them by name and its button opens
  their own aOS invite; `welcome/#make` turns a name and an aOS invite link into that welcome link.
  Everything after the # stays in the browser.
  https://tomallison24.github.io/aos-teaser/welcome/

Published with GitHub Pages. Add `?export` to either page to drive it frame by frame (`window.renderAt(t)`).
