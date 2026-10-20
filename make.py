#!/usr/bin/env python3
"""ANANEOSI — build a «we're renewing» page for any client.

    python3 make.py <folder>        e.g.  python3 make.py vasileiadou

<folder>/config.json holds everything client-specific (see vasileiadou/config.json).
<folder>/ must also contain: the logo SVG, assets/img/* (hero photo of the space, og.jpg, logo svg), assets/fonts/*.woff2,
and optionally assets/icons/* (favicon set) + favicon.ico.
Writes <folder>/index.html and <folder>/privacy.html. The folder is self-contained, so it can
be served on its own (e.g. put on the client's domain while their new site is being finished).
"""
import json, re, sys, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
TPL = ROOT / "_template"
E = html.escape

ICON = {"phone": "i-phone", "mobile": "i-mobile", "email": "i-mail", "address": "i-pin"}
GO = {"phone": "Καλέστε", "mobile": "Καλέστε", "email": "Στείλτε email", "address": "Οδηγίες στον χάρτη"}


def logo_parts(svg_text):
    vb = re.search(r'viewBox="([^"]+)"', svg_text).group(1)
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", svg_text.strip(), flags=re.S)
    inner = re.sub(r'fill="(?!none)[^"]*"', 'fill="currentColor"', inner)
    stroke = re.sub(r"<path ", '<path pathLength="1" ', inner)
    return vb, inner, stroke


def hex_rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def build(folder):
    folder = (ROOT / folder).resolve()
    c = json.loads((folder / "config.json").read_text(encoding="utf-8"))
    col, fonts = c["colors"], c["fonts"]
    vb, paths, paths_stroke = logo_parts((folder / c["logo_svg"]).read_text(encoding="utf-8"))

    faces, preloads = [], []
    for f in fonts["faces"]:
        faces.append("@font-face{font-family:'%s';src:url(%s) format('woff2');font-weight:%s;font-style:%s;font-display:swap;unicode-range:%s}"
                     % (f["family"], f["file"], f.get("weight", 400), f.get("style", "normal"), f["range"]))
        if f.get("preload"):
            preloads.append('<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' % f["file"])

    icons = []
    if (folder / "assets/icons/favicon.svg").exists():
        icons.append('<link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">')
    for s in (96, 48, 32):
        if (folder / f"assets/icons/favicon-{s}.png").exists():
            icons.append(f'<link rel="icon" href="assets/icons/favicon-{s}.png" sizes="{s}x{s}" type="image/png">')
    if (folder / "assets/icons/apple-touch-icon.png").exists():
        icons.append('<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">')

    contacts = c["contacts"]
    primary = next(x for x in contacts if x["type"] in ("phone", "mobile"))
    email = next((x for x in contacts if x["type"] == "email"), None)
    address = next((x for x in contacts if x["type"] == "address"), None)

    cards = []
    for i, x in enumerate(contacts):
        ext = x["type"] == "address"
        long_val = len(x["value"]) > 22
        cards.append(
            '<a class="card" style="--k:%d" href="%s"%s><span class="ic"><svg aria-hidden="true"><use href="#%s"/></svg></span>'
            '<small>%s</small><strong%s>%s</strong><span class="go">%s<svg aria-hidden="true"><use href="#i-arrow"/></svg></span></a>'
            % (i, E(x["href"]), ' target="_blank" rel="noopener"' if ext else "", ICON[x["type"]], E(x["label"]),
               ' class="sm"' if long_val else "", E(x["value"]).replace("@", "<wbr>@"), E(x.get("action", GO[x["type"]]))))

    rows = []
    for i, x in enumerate(contacts):
        ext = x["type"] == "address"
        long_val = len(x["value"]) > 22
        rows.append(
            '<a class="row" style="--k:%d" href="%s"%s><span class="ic"><svg aria-hidden="true"><use href="#%s"/></svg></span>'
            '<small>%s</small><strong%s>%s</strong><svg class="ar" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
            % (i, E(x["href"]), ' target="_blank" rel="noopener"' if ext else "", ICON[x["type"]], E(x["label"]),
               ' class="sm"' if long_val else "", E(x["value"]).replace("@", "<wbr>@")))
    psi_tiny = '<svg viewBox="%s" aria-hidden="true"><use href="#psi"/></svg>' % vb
    tick_items = "".join("<span>%s</span>%s" % (E(s), psi_tiny) for s in c["services"])
    ticker = '<div class="r">%s</div><div class="r" aria-hidden="true">%s</div>' % (tick_items, tick_items)

    psi_small = '<svg viewBox="%s" aria-hidden="true"><use href="#psi"/></svg>' % vb
    row_items = "".join("<span>%s</span>%s" % (E(s), psi_small) for s in c["services"])
    band_row = '<div class="row">%s</div>' % row_items
    band_hidden = '<div class="row" aria-hidden="true">%s</div>' % row_items

    steps = "".join('<li class="step"><span class="dot">%d</span><div class="t"><h3>%s</h3><p>%s</p></div></li>'
                    % (i + 1, E(s["title"]), E(s["text"])) for i, s in enumerate(c.get("steps", [])))

    r = c.get("rating")
    rating = ""
    if r:
        rating = ('<a class="gr" href="%s" target="_blank" rel="noopener"><svg class="gmark" aria-hidden="true"><use href="#g"/></svg>'
                  '<b>%s</b><span class="stars" aria-hidden="true">%s</span><span class="sr">αξιολόγηση στο Google</span></a>'
                  % (E(r["url"]), E(r["value"]), '<svg><use href="#star"/></svg>' * 5))

    mbar = ['<a href="%s"><svg aria-hidden="true"><use href="#i-phone"/></svg>Κλήση</a>' % E(primary["href"])]
    if email:
        mbar.append('<a href="%s"><svg aria-hidden="true"><use href="#i-mail"/></svg>Email</a>' % E(email["href"]))
    if address:
        mbar.append('<a href="%s" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-pin"/></svg>Οδηγίες</a>' % E(address["href"]))

    footer_links = "".join('<a href="%s">%s</a>' % (E(x["href"]), E(x["value"])) for x in contacts if x["type"] in ("phone", "mobile", "email"))

    # closing line: «…» parts wrapped in *stars* become <em>
    closing = re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(c.get("closing", "")))

    hero, photo = c["hero"], c.get("photo", {"src": "", "alt": "", "w": 1, "h": 1, "caption": ""})
    v = {
        "TITLE": E(c["title"]), "DESCRIPTION": E(c["description"]), "OG_IMAGE": E(c.get("og_image", hero["desktop"])),
        "ICONS": "\n".join(icons), "FONT_PRELOADS": "\n".join(preloads), "FONTFACES": "\n".join(faces),
        "C_PAPER": col["paper"], "C_PAPER2": col["paper2"], "C_PAPER3": col["paper3"], "C_INK": col["ink"], "C_INK2": col["ink2"],
        "C_BRAND": col["brand"], "C_ACC": col["acc"], "C_ACC2": col["acc2"], "C_GLOW": col["glow"], "C_DARK": col["dark"], "C_DARK2": col["dark2"],
        "DUST_RGB": hex_rgb(col.get("dust", col["glow"])),
        "F_SERIF": fonts["serif"], "F_SANS": fonts["sans"],
        "LOGO_VIEWBOX": vb, "LOGO_PATHS": paths, "LOGO_PATHS_STROKE": paths_stroke,
        "NAME": E(c["name"]), "ROLE": E(c["role"]), "ROLE_SHORT": E(c.get("role_short", c["role"])),
        "HERO_D": E(hero["desktop"]), "HERO_M": E(hero["mobile"]), "HERO_W": str(hero["w"]), "HERO_H": str(hero["h"]),
        "HERO_ALT": E(hero["alt"]), "HERO_POS": hero.get("position", "50% 50%"), "HERO_POS_M": hero.get("position_mobile", "50% 50%"),
        "BEAM_X": hero.get("beam_x", "6vw"),
        "STATUS": E(c["status"]), "EYEBROW": E(c["eyebrow"]), "HEADLINE": E(c["headline"]), "HEADLINE_EM": E(c["headline_em"]),
        "LEDE": E(c["lede"]), "CTA_PRIMARY": E(c["cta_primary"]), "CTA_SECONDARY": E(c["cta_secondary"]), "ETA": E(c["eta"]),
        "RATING_CHIP": rating,
        "PRIMARY_HREF": E(primary["href"]), "PRIMARY_TXT": E(primary["value"]),
        "EMAIL_HREF": E(email["href"]) if email else "#", "EMAIL_TXT": E(email["value"]) if email else "",
        "ADDRESS_TEXT": E(address["value"]) if address else "",
        "BAND_LABEL": E(c.get("band_label", "Υπηρεσίες")), "BAND_ROW": band_row, "BAND_ROW_HIDDEN": band_hidden,
        "CONTACT_KICKER": E(c["contact_kicker"]), "CONTACT_TITLE": re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(c["contact_title"])),
        "CONTACT_TEXT": E(c["contact_text"]), "NOTE": re.sub(r"\*(.+?)\*", r"<b>\1</b>", E(c["note"])),
        "PHOTO": E(photo["src"]), "PHOTO_ALT": E(photo["alt"]), "PHOTO_W": str(photo["w"]), "PHOTO_H": str(photo["h"]),
        "PHOTO_CAPTION": E(photo["caption"]), "CARDS": "".join(cards), "ROWS": "".join(rows), "TICKER": ticker,
        "BADGE": E(c.get("badge", "ΝΕΑ ΙΣΤΟΣΕΛΙΔΑ · ΣΥΝΤΟΜΑ · ")),
        "ROAD_KICKER": E(c.get("road_kicker", "")), "ROAD_TITLE": E(c.get("road_title", "")), "STEPS": steps,
        "CLOSING": closing, "CLOSING_LABEL": E(c.get("closing_label", "Ευχαριστούμε")),
        "FOOTER_LINKS": footer_links, "MBAR": "".join(mbar),
        "JSONLD": json.dumps(c["schema"], ensure_ascii=False),
        "UPDATED": datetime.date.today().strftime("%d/%m/%Y"), "YEAR": str(datetime.date.today().year),
    }

    def fill(t):
        out = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: v[m.group(1)], t)
        left = re.findall(r"\{\{[A-Z0-9_]+\}\}", out)
        if left:
            sys.exit("missing values: %s" % left)
        return out

    (folder / "index.html").write_text(fill((TPL / "index.html").read_text(encoding="utf-8")), encoding="utf-8")
    (folder / "privacy.html").write_text(fill((TPL / "privacy.html").read_text(encoding="utf-8")), encoding="utf-8")
    print("built", folder / "index.html")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    build(sys.argv[1])
