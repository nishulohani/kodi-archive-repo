import sys, json, urllib.parse, urllib.request
import xbmcgui, xbmcplugin

H = int(sys.argv[1]); BASE = sys.argv[0]
Q = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))

def get(u):
    with urllib.request.urlopen(u) as r:
        return json.load(r)

def link(**kw):
    return BASE + "?" + urllib.parse.urlencode(kw)

def menu():
    for label, col in (("Movies", "feature_films"), ("Audio", "opensource_audio")):
        xbmcplugin.addDirectoryItem(H, link(a="list", c=col), xbmcgui.ListItem(label), True)

def listing(col):
    u = ("https://archive.org/advancedsearch.php?q=collection:" + col +
         "&fl[]=identifier&fl[]=title&rows=50&output=json")
    for d in get(u)["response"]["docs"]:
        li = xbmcgui.ListItem(d.get("title", d["identifier"]))
        xbmcplugin.addDirectoryItem(H, link(a="files", i=d["identifier"]), li, True)

def files(i):
    for f in get("https://archive.org/metadata/" + i)["files"]:
        if f["name"].lower().endswith((".mp4", ".mkv", ".ogv", ".mp3", ".flac", ".ogg")):
            li = xbmcgui.ListItem(f["name"])
            li.setProperty("IsPlayable", "true")
            u = "https://archive.org/download/%s/%s" % (i, urllib.parse.quote(f["name"]))
            xbmcplugin.addDirectoryItem(H, u, li, False)

a = Q.get("a")
if a == "list": listing(Q["c"])
elif a == "files": files(Q["i"])
else: menu()
xbmcplugin.endOfDirectory(H)
