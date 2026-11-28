"""Wrap index.html (the Claude artifact body) into play.html, a full standalone page
for GitHub Pages / iPhone home screen. Run after every change: python3 build_play.py"""
import pathlib
here = pathlib.Path(__file__).parent
src = (here / "index.html").read_text()
# index.html opens with its head material (title, meta, fonts, style); the page itself
# starts at the canvas
cut = src.index("<canvas")
head_part, body = src[:cut].rstrip() + "\n", src[cut:]
head_part = head_part.replace('<meta charset="utf-8">\n', "", 1)  # the head below has it
head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Firefly Jar">
<meta name="theme-color" content="#06070c">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="manifest" href="manifest.json">
<script>window.FJ_PAGES = true;</script>
"""
# After the game's own styles: no Claude app around the page, so the safe areas come
# straight from iOS, and the --sh-* shifts (set by placeTop) centre things on the real
# screen when the phone keeps a strip of it for the clock and battery.
overrides = """<style>
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html,body{background:#06070c;margin:0;width:100%;overflow:hidden}
canvas{left:0!important;top:0!important;width:100vw!important;height:100lvh!important}
.overlay{--sym:max(16px,env(safe-area-inset-left,0px),env(safe-area-inset-right,0px));padding-left:calc(var(--sym) + var(--sh-ov-l,0px))!important;padding-right:calc(var(--sym) + var(--sh-ov-r,0px))!important}
.hud{padding-left:calc(16px + var(--sh-hud-l,0px))!important;padding-right:calc(16px + var(--sh-hud-r,0px))!important}
.scene-ui{padding-left:calc(max(16px,env(safe-area-inset-left,0px)) + var(--sh-cap-l,0px))!important;padding-right:calc(max(16px,env(safe-area-inset-right,0px)) + var(--sh-cap-r,0px))!important}
</style>
</head>
<body>
"""
(here / "play.html").write_text(head + head_part + overrides + body + "\n</body>\n</html>\n")
print("wrote play.html")
