# -- coding: utf-8 --
from util import hook, http
import re, HTMLParser, urllib, time, requests

def _search(inp, say):
    url = "http://duckduckgo.com/lite?"+urllib.urlencode({"q":inp.encode('utf8', 'ignore')})
    try:
        data = http.get(url)
    except http.HTTPError, e:
        say(str(e)+": "+url)
        return
    data = re.sub("\s+"," ", data)
    search = re.search("""<td valign="top">1.&nbsp;<\/td> <td> <a rel="nofollow" href="(.*?)" class='result-link'>(.*?)<\/a> <\/td> <\/tr> <tr> <td>&nbsp;&nbsp;&nbsp;<\/td> <td class='result-snippet'>(.*?)<\/td> <\/tr> <tr> <td>&nbsp;&nbsp;&nbsp;<\/td> <td> <span class='link-text'>(.*?)<\/span> <\/td> <\/tr>""",data)
    if search:
        resultdesc = re.sub('<[^<]+?>', '', search.group(3)[0:180].decode('utf8', 'ignore').strip()+"...")
        resulturl  = "\00312"+HTMLParser.HTMLParser().unescape(search.group(1))+"\003"
        resultdesc = HTMLParser.HTMLParser().unescape(resultdesc)
        say(resultdesc+" - "+resulturl)
    else:
        say("No results found.")

@hook.command
def tld(inp):
    "tld <tdl> -- returns info about the tld"
    if inp.startswith("."): _tld = inp[1:]
    else: _tld = inp
    if "." in _tld: _tld = _tld.split(".")[-1]
    try:
        data = http.get("http://www.iana.org/domains/root/db/%s.html"%_tld.encode("utf8","ignore"))
    except http.HTTPError, e:
        if "404:" in str(e):
            try:
                data = http.get("https://en.wikipedia.org/wiki/.%s"%_tld.encode("utf8","ignore"))
            except http.HTTPError, e:
                return "No match for %s"%_tld
            search = re.search("""<th scope="row" style="text-align:left;">Sponsor<\/th>\n<td><a href="(.*)" title="(.*)">(.*)<\/a><\/td>""",data)
            if search:
                return "TLD: %s - Sponsor: %s"%(_tld,HTMLParser.HTMLparser().unescape(search.group(3)))
            else:
                return "No match for %s"%_tld
        else:
            return "No match for %s"%_tld
    search = re.search("""<b>(.*)<\/b><br\/>""",data)
    if search:
        sponsor = re.sub('<[^<]+?>', ' ', search.group(1))
        return "TLD: %s - Sponsor: %s"%(_tld.encode("utf8","ignore"),sponsor)

@hook.command
def expand(inp, say=None):
    "expand <url> -- expands short URLs"
    try:
        return (http.open(inp).url.strip())
    except http.URLError, e:
        return ("Unable to expand")

@hook.regex("(.*)>\?\s?(.*)")
def zeroclick(inp, say=None, input=None):
    "zeroclick/0click <search> -- gets zero-click info from DuckDuckGo"
    if inp.group(2) != "":
        if inp.group(2).lower() == "what is love":
            return "http://youtu.be/xhrBDcQq2DM"
        url = "http://duckduckgo.com/lite?"
        params = {"q":inp.group(2).replace("\001","").encode('utf8', 'ignore')}
        url = "http://duckduckgo.com/lite/?"+urllib.urlencode(params)
        try:
            data = http.get(url).decode("utf-8","ignore")
        except http.HTTPError, e:
            say(str(e)+": "+url)
            return
        #search = re.findall("""\t<td>.\t\s+(.*?).\t<\/td>""",data,re.M|re.DOTALL)
        m = re.findall("\t<td>.\t\s+(.*?).\t<\/td>",data,re.M|re.DOTALL)
        if len(m) == 1:
            search = re.sub("\s+"," ", re.sub('<[^<]+?>',' ',m[0]))
        else:
            search = None
        if search:
            out = HTMLParser.HTMLParser().unescape(search.replace("<br>"," ").replace("<code>","\002").replace("</code>","\002"))
            if out: say(u"\x0302\x02ǁ\x02\x03 {}".format(out.split(" [ More at")[0].split("}")[-1].strip()))
            else: say(u"\x0302\x02ǁ\x02\x03 No results")
        else:
            say(u"\x0302\x02ǁ\x02\x03 No results found.")

@hook.command
def ddg(inp, say=None):
    "ddg <search> -- search DuckDuckGo"
    _search(inp, say)

@hook.command('sc')
@hook.command
def soundcloud(inp, say=None):
    "soundcloud/sc <search> -- search SoundCloud for music"
    _search(inp+" site:soundcloud.com", say)

@hook.command
def reddit(inp, say=None):
    "reddit <search> -- search reddit"
    _search(inp+" site:reddit.com", say)

@hook.command("gp")
@hook.command
def googleplay(inp, say=None):
    "googleplay/gp <search> -- search Google Play"
    _search(inp+" site:play.google.com", say)

@hook.command("ff")
@hook.command
def firefox(inp, say=None):
    "firefox/ff <search> -- search for Firefox addons"
    _search(inp+" site:addons.mozilla.org", say)

@hook.command
def amazon(inp, say=None):
    _search(inp+" site:amazon.com", say)

@hook.command
def archwiki(inp, say=None):
    "arch/archwiki <search> -- search arch wikipedia"
    _search(inp+" site:wiki.archlinux.org", say)

@hook.command
def dimg(inp, say=None):
    "dimg <search> -- search DuckDuckGo images"
    url = "http://duckduckgo.com/i.js?"+urllib.urlencode({"q":inp,"o":"json"})
    try:
        data = requests.get(url).json()
    except:
        return "Could not find image"
    return data["results"][0]["image"]

@hook.command
def qrcode(inp, input=None):
    "Usage: qrcode <text/url/number>"
    return "http://chart.apis.google.com/chart?cht=qr&chs=300x300&{}".format(urllib.urlencode({"chl":inp}))

@hook.command
def berkin(inp):
    return requests.post("http://berkin.me/probox/run",data={"nsfw":"true","code":inp}).json()["result"]

@hook.command
def porn(inp, say=None):
    #"Usage: porn [-gay|-straight|-shemale] <search>"
    if "-gay" in inp or "-straight" in inp or "-shemale" in inp:
        t,s = inp.split(" ",1)
    else:
        t = "gay"
        s = inp
    if t and s:
        p = requests.get("http://www.pornmd.com/{}/{}?start=0&ajax=true&limit=1&format=json".format(t.replace("-","").replace("shemale","tranny"),s))
        if p.ok:
            link = requests.get("http://www.pornmd.com{}".format(p.json()["videos"][0]["link"])).url
            p = p.json()
            if "gay" in p["videos"][0]["keywords"][0]["link"]: gss = "Gay"
            if "straight" in p["videos"][0]["keywords"][0]["link"]: gss = "Straight"
            if "tranny" in p["videos"][0]["keywords"][0]["link"]: gss = "Shemale"
            output = u"{} [{}] - {}% - {} - {} - {}".format(p["videos"][0]["title"],gss,p["videos"][0]["rating"],p["videos"][0]["pub_date"],p["videos"][0]["source"],link)
            return output
        else:
            return "404 not found, {}".format(porn.__doc__)
    else:
        return porn.__doc__
