#!/usr/bin/env python3
import json, urllib.parse, urllib.request
from collections import defaultdict
COLLECTION="aadamjacobs"
ROWS=10000
def fetch_json(url):
    req=urllib.request.Request(url, headers={"User-Agent":"ArchiveMusicLibrary/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))
def search_items():
    q=urllib.parse.quote(f'collection:({COLLECTION})')
    url=("https://archive.org/advancedsearch.php"
         f"?q={q}&fl[]=identifier&fl[]=title&rows={ROWS}&page=1&output=json")
    return fetch_json(url)["response"]["docs"]
def guess_artist(title):
    for sep in [" - "," – ","_ ",": "]:
        if sep in title:
            return title.split(sep,1)[0].strip()
    return title.strip()
def fallback_image(artist):
    encoded=urllib.parse.quote(artist)
    return f"https://ui-avatars.com/api/?name={encoded}&size=800&background=1f2937&color=ffffff&bold=true"
def fetch_artist_image(artist):
    try:
        q=urllib.parse.quote(artist)
        data=fetch_json(f"https://itunes.apple.com/search?term={q}&entity=musicArtist&limit=1")
        if data.get("results"):
            artist_id=data["results"][0].get("artistId")
            if artist_id:
                lookup=fetch_json(f"https://itunes.apple.com/lookup?id={artist_id}&entity=album&limit=1")
                for result in lookup.get("results",[]):
                    if "artworkUrl100" in result:
                        return result["artworkUrl100"].replace("100x100bb","1200x1200bb")
    except Exception:
        pass
    return fallback_image(artist)
def main():
    grouped=defaultdict(list)
    for doc in search_items():
        identifier=doc["identifier"]
        title=doc.get("title") or identifier
        artist=guess_artist(title)
        grouped[artist].append({"title":title,"url":f"https://archive.org/details/{identifier}"})
    output=[]
    for artist in sorted(grouped, key=str.lower):
        output.append({"artist":artist,"image":fetch_artist_image(artist),"links":grouped[artist]})
    with open("artists.json","w",encoding="utf-8") as f:
        json.dump(output,f,ensure_ascii=False,indent=2)
    print(f"{len(output)} artistes générés.")
if __name__=="__main__":
    main()
