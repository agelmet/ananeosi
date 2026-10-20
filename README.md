# ananeosi — «Η ιστοσελίδα μας ανανεώνεται»

A reusable, animated holding page for any Advon client whose site is down / being renewed.
Each client gets its own self-contained folder (it can be served on its own, e.g. on the client's domain).

Live drafts: `https://drafts.advonmedia.com/ananeosi/<folder>/`

## New client in 5 steps
1. Copy `vasileiadou/` to `<surname>/`.
2. Replace `assets/img/*` (hero photo of the space, a second photo shown whole, `og.jpg` 1200×630, logo SVG), `assets/fonts/*` (the client's Greek-capable fonts) and `assets/icons/*` (favicon set from the logo — `.advon/favicon.py`).
3. Edit `<surname>/config.json` — name, role, colours, contacts, services, steps, texts, schema. `*word*` in titles/closing = highlighted word.
4. `python3 make.py <surname>` → writes `index.html` + `privacy.html`.
5. Commit + push → GitHub Pages updates the draft link (0 Netlify credits).

What it has (v2, one screen, no scrolling — 20 Oct 2026): window-blinds intro with the logo, full-screen photo of the client's space with slow zoom + drift, sunbeams, sunlight dust, a mouse-following light and parallax, word-by-word headline with drawn underline, «open as usual» pulse badge, frosted contact panel that swings in (3D tilt on the mouse) with all contacts, a rotating «ΝΕΑ ΙΣΤΟΣΕΛΙΔΑ · ΣΥΝΤΟΜΑ» seal, a services ticker, renewal progress line, Google rating chip, privacy link + Advon credit. Fits one screen from small phones to big monitors (very short screens may scroll instead of cutting content). No cookies, nothing loaded from third parties, reduced-motion respected.
