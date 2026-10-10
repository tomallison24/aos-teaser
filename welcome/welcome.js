// The welcome: a joke in the dark, the punchline turning into aOS, then day.
//   welcome/                         the welcome, with a button that opens aOS
//   welcome/#name=Sarah&invite=CODE  says hello to Sarah, and her button opens her own invite
//                                    (the code from aOS's invite link, …/aOS/#invite=CODE)
//   welcome/#make                    for the owner: paste a name and an aOS invite link, get the welcome link
// Everything rides after the #, so the name and the invite never reach a server.
(() => {
  'use strict';
  const AOS = 'https://tomallison24-news.pages.dev/aOS/';
  // the core apps, then the Allison family's own (as aOS shows them)
  const CORE = ['weather', 'notes', 'news', 'mail', 'calendar'], FAMILY = ['podcasts', 'travel', 'places', 'fitness', 'drinks', 'meals', 'house'];
  const HUES = ['#6EA2B7', '#6FA597', '#A08D7B', '#7F93C2', '#C08A84', '#8D84BE', '#C9976E', '#8FA570', '#6B7F91', '#A97590', '#B5705A', '#BC9C68'];
  const $ = id => document.getElementById(id);
  const body = document.body;
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hash = new URLSearchParams(location.hash.slice(1));
  const tokenOf = s => { s = String(s || '').trim(); const m = /[#&?]invite=([A-Za-z0-9_-]+)/.exec(s); return m ? m[1] : /^[A-Za-z0-9_-]{12,}$/.test(s) ? s : null; };
  const cleanName = s => String(s || '').replace(/\s+/g, ' ').trim().slice(0, 40);
  addEventListener('hashchange', () => location.reload());

  // ---- making a link ----
  if (hash.has('make')) {
    body.classList.add('making', 'day');
    const name = $('mName'), inv = $('mInvite'), out = $('mOut'), err = $('mErr');
    const make = () => {
      err.textContent = '';
      const t = tokenOf(inv.value);
      if (!t) { err.textContent = 'Paste the invite link from aOS (it has #invite= in it).'; return null; }
      const q = new URLSearchParams(); if (cleanName(name.value)) q.set('name', cleanName(name.value)); q.set('invite', t);
      const link = location.origin + location.pathname + '#' + q;
      out.textContent = link; out.hidden = false;
      return link;
    };
    $('maker').addEventListener('submit', async e => {
      e.preventDefault();
      const link = make(); if (!link) return;
      const who = cleanName(name.value);
      if (navigator.share) { try { await navigator.share({ title: 'Your wait is over', text: `${who ? who + ', y' : 'Y'}our wait is over. Welcome to the aOS family.`, url: link }); } catch {} }
      else $('mCopy').click();
    });
    $('mCopy').addEventListener('click', async () => {
      const link = make(); if (!link) return;
      try { await navigator.clipboard.writeText(link); $('mCopy').textContent = 'Copied'; } catch { $('mCopy').textContent = 'Press and hold the link'; }
    });
    return;
  }

  // ---- who it's for, and where their button goes ----
  const name = cleanName(hash.get('name')), token = tokenOf(hash.get('invite'));
  if (name) {
    const hi = $('hi'); hi.textContent = 'Welcome to the aOS ';
    const em = document.createElement('em'); em.textContent = 'family'; hi.append(em, `, ${name}.`);
  }
  if (token) {
    $('go').href = AOS + '#invite=' + token;
    $('note').textContent = 'Next: Face ID (or your fingerprint) makes your account, then aOS shows you how to add it to your Home Screen. Open this on your phone, in Safari on iPhone or Chrome on Android. Your invite works once, within 24 hours of when it was sent.';
  }
  const apps = $('apps');
  [...CORE, ...FAMILY].forEach((id, i) => {
    const im = new Image(); im.src = `../launch/icons/${id}.webp`; im.alt = ''; im.style.transitionDelay = (1.1 + i * .05 + (i >= CORE.length ? .15 : 0)) + 's';
    $(i < CORE.length ? 'coreIcons' : 'familyIcons').appendChild(im);
  });

  // ---- the joke, then day ----
  let timers = [];
  const at = (ms, fn) => timers.push(setTimeout(fn, ms));
  function confetti() {
    const box = document.querySelector('.bits'); box.textContent = '';
    if (still) return;
    for (let i = 0; i < 70; i++) {
      const b = document.createElement('i'), an = Math.random() * Math.PI * 2, r = 30 + Math.random() * 55, rot = (Math.random() - .5) * 900;
      b.style.background = HUES[i % HUES.length];
      if (i % 3 === 0) { b.style.width = b.style.height = '8px'; b.style.borderRadius = '50%'; }
      box.appendChild(b);
      b.animate([
        { opacity: 1, transform: 'translate(-50%, -50%) rotate(0deg)' },
        { opacity: 1, transform: `translate(calc(-50% + ${Math.cos(an) * r}vmin), calc(-50% + ${Math.sin(an) * r - 10}vmin)) rotate(${rot / 2}deg)`, offset: .45 },
        { opacity: 0, transform: `translate(calc(-50% + ${Math.cos(an) * r * 1.15}vmin), calc(-50% + ${Math.sin(an) * r + 45}vmin)) rotate(${rot}deg)` },
      ], { duration: 2600 + Math.random() * 1400, easing: 'cubic-bezier(.2,.7,.4,1)', fill: 'forwards' });
    }
  }
  function toDay() {
    timers.forEach(clearTimeout); timers = [];
    ['q', 'a', 'word'].forEach(id => $(id).classList.add('on'));
    $('word').classList.add('drop', 'turn');
    body.classList.add('day'); apps.classList.add('on');
  }
  function play() {
    timers.forEach(clearTimeout); timers = [];
    body.classList.remove('day'); apps.classList.remove('on');
    ['q', 'a', 'word'].forEach(id => $(id).classList.remove('on', 'drop', 'turn'));
    scrollTo(0, 0);
    if (still) return toDay();
    at(500, () => $('q').classList.add('on'));
    at(2300, () => $('a').classList.add('on'));
    at(3400, () => $('word').classList.add('on'));
    at(4300, () => $('word').classList.add('drop'));
    at(5400, () => $('word').classList.add('turn'));
    at(5700, confetti);
    at(7300, () => { body.classList.add('day'); apps.classList.add('on'); });
  }
  $('skip').addEventListener('click', toDay);
  $('again').addEventListener('click', play);
  play();
})();
