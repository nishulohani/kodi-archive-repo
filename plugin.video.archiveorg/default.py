import sys, json, urllib.parse, urllib.request
import xbmcgui, xbmcplugin

H = int(sys.argv[1]); BASE = sys.argv[0]
Q = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
ROWS = 50
API = "https://archive.org/advancedsearch.php"
EXT = (".mp4", ".mkv", ".ogv", ".avi", ".webm", ".mp3", ".flac", ".ogg", ".m4a")

VIDEO = [("All Movies", "movies"), ("Feature Films", "feature_films"),
         ("Classic TV", "classic_tv"), ("Cartoons & Animation", "animationandcartoons"),
         ("Silent Films", "silent_films"), ("Film Noir", "film_noir"),
         ("Community Video", "opensource_movies"), ("Prelinger Archives", "prelinger")]
AUDIO = [("All Audio", "audio"), ("Community Audio", "opensource_audio"),
         ("Live Music Archive", "etree"), ("Old Time Radio", "oldtimeradio"),
         ("Music", "audio_music")]

def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Kodi-ArchiveOrg/1.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def link(**kw):
    return BASE + "?" + urllib.parse.urlencode(kw)

def folder(label, url):
    xbmcplugin.addDirectoryItem(H, url, xbmcgui.ListItem(label), True)

def note(msg):
    xbmcgui.Dialog().notification("Archive.org", msg)

def menu():
    folder("Search Videos", link(a="search", k="movies"))
    folder("Search Audio", link(a="search", k="audio"))
    folder("Video Collections", link(a="cols", k="video"))
    folder("Audio Collections", link(a="cols", k="audio"))
    folder("Enter Any Collection ID", link(a="custom"))

def cols(kind):
    for label, cid in (VIDEO if kind == "video" else AUDIO):
        folder(label, link(a="browse", q='collection:"%s"' % cid, p=1))

def search(kind):
    text = xbmcgui.Dialog().input("Search archive.org")
    if not text:
        return False
    q = "(%s) AND mediatype:(%s)" % (text, kind)
    browse(q, 1)
    return True

def custom():
    cid = xbmcgui.Dialog().input("Collection ID (the last part of the archive.org/details/ URL)")
    if not cid:
        return False
    browse('collection:"%s"' % cid.strip(), 1)
    return True

def browse(q, page):
    params = [("q", q), ("fl[]", "identifier"), ("fl[]", "title"),
              ("rows", ROWS), ("page", page), ("sort[]", "downloads desc"),
              ("output", "json")]
    try:
        resp = get(API + "?" + urllib.parse.urlencode(params))["response"]
    except Exception as e:
        note("Error: %s" % e)
        return
    docs = resp.get("docs", [])
    if not docs:
        note("Nothing found")
        return
    for d in docs:
        i = d["identifier"]
        li = xbmcgui.ListItem(d.get("title", i))
        li.setArt({"thumb": "https://archive.org/services/img/" + i})
        xbmcplugin.addDirectoryItem(H, link(a="files", i=i), li, True)
    total = resp.get("numFound", 0)
    if page * ROWS < total:
        pages = (total + ROWS - 1) // ROWS
        folder("Next page (%d of %d)  >>" % (page + 1, pages), link(a="browse", q=q, p=page + 1))

def files(i):
    try:
        data = get("https://archive.org/metadata/" + i)
    except Exception as e:
        note("Error: %s" % e)
        return
    for f in data.get("files", []):
        if f["name"].lower().endswith(EXT):
            label = f["name"]
            if f.get("size", "").isdigit():
                label += "  (%d MB)" % (int(f["size"]) // 1048576)
            li = xbmcgui.ListItem(label)
            li.setProperty("IsPlayable", "true")
            li.setArt({"thumb": "https://archive.org/services/img/" + i})
            u = "https://archive.org/download/%s/%s" % (i, urllib.parse.quote(f["name"]))
            xbmcplugin.addDirectoryItem(H, u, li, False)

a = Q.get("a")
ok = True
if a == "cols": cols(Q["k"])
elif a == "search": ok = search(Q["k"])
elif a == "custom": ok = custom()
elif a == "browse": browse(Q["q"], int(Q.get("p", 1)))
elif a == "files": files(Q["i"])
else: menu()
xbmcplugin.endOfDirectory(H, succeeded=bool(ok))
