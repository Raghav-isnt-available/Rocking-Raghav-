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
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
</head>
<body>
"""
(here / "play.html").write_text(head + body + "\n</body>\n</html>\n")
print("wrote play.html")
