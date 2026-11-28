"""Wrap index.html (the Claude artifact body) into play.html, a full standalone page
for GitHub Pages / iPhone home screen. Run after every change: python3 build_play.py"""
import pathlib
here = pathlib.Path(__file__).parent
body = (here / "index.html").read_text()
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
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html,body{background:#06070c;margin:0;width:100%;overflow:hidden}[hidden]{display:none!important}
canvas{left:0!important;top:0!important;right:0!important;bottom:0!important;width:100vw!important;height:100lvh!important}
.overlay{--sym:max(16px,env(safe-area-inset-left,0px),env(safe-area-inset-right,0px));padding-left:var(--sym)!important;padding-right:var(--sym)!important}
.hud{padding-left:16px!important;padding-right:16px!important}
.overlay,.hud,.scene-ui,.bar{right:calc(-1 * var(--extra-w,0px))!important}</style>
</head>
<body>
"""
(here / "play.html").write_text(head + body + "\n</body>\n</html>\n")
print("wrote play.html")
