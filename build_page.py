import os
import re

SONGS_ROOT = "./songs"
OUTPUT_FILE = "index.html"

NORM_DICT : dict = {
    'č' : 'c',
    'Č' : 'C',
    'ď' : 'd',
    'Ď' : 'D',
    'ň' : 'n',
    'Ň' : 'N',
    'ť' : 't',
    'Ť' : 'T',
    'ř' : 'r',
    'Ř' : 'R',
    'š' : 's',
    'Š' : 'S',
    'ž' : 'z',
    'Ž' : 'Z',
    'ó' : 'o',
    'Ó' : 'O',
    'á' : 'a',
    'Á' : 'A',
    'é' : 'e',
    'É' : 'E',
    'ě' : 'e',
    'Ě' : 'E',
    'í' : 'i',
    'Í' : 'I',
    'ů' : 'u',
    'Ů' : 'U',
    'ú' : 'u',
    'Ú' : 'U',
    'ý' : 'y',
    'Ý' : 'Y'
}

def normalize_string(text : str) -> str:
    res = ''
    for c in text:
        if c in NORM_DICT.keys():
            res+=NORM_DICT[c]
        else:
            res+=c
    return res

def sanitize_anchor(name):
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "-")
                
def generate_html():
    all_songs = {}

    for dirpath, _, filenames in os.walk(SONGS_ROOT):
        rel_path = os.path.relpath(dirpath, SONGS_ROOT)
        if rel_path == ".":
            continue 

        category = rel_path
        song_files = [f for f in filenames]
        if not song_files:
            continue

        all_songs[category] = []
        for fname in sorted(song_files, key=lambda x: normalize_string(x)):
            song_path = os.path.join(dirpath, fname)
            title = os.path.splitext(fname)[0]
            with open(song_path, encoding="utf-8") as f:
                lyrics = f.read()
            all_songs[category].append((title, lyrics))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("<!DOCTYPE html>\n<html>\n<head>\n")
        out.write("<meta charset='utf-8'>\n<title>Zpěvník</title>\n")
        out.write("""
<link rel="stylesheet" href="./style.css">
<script>

function highlight(text, term) {
    const escTerm = term.replace(/[.*+?^${}()|[\\\\\\]]/g, '\\\\$&');
    const regex = new RegExp(escTerm, 'gi');
    return text.replace(regex, match => '<mark>' + match + '</mark>');
}

function filterSongs() {
    const q = document.getElementById('searchbar').value.trim().toLowerCase();
    const songBlocks = document.querySelectorAll('.song-block');
    const indexLinks = document.querySelectorAll('.index-link>a');

    let firstVisible = null;

    songBlocks.forEach(block => {
        const rawTitle = block.querySelector('h3').textContent.toLowerCase();
        const rawLyrics = block.querySelector('pre').textContent.toLowerCase();

        const match = rawTitle.includes(q) || rawLyrics.includes(q);
        block.style.display = match ? 'block' : 'none';

        const h3 = block.querySelector('h3');
        const pre = block.querySelector('pre');
        const titleText = h3.textContent;
        const lyricsText = pre.textContent;

        
        h3.innerHTML = match ? highlight(titleText, q) : titleText;
        pre.innerHTML = match ? highlight(lyricsText, q) : lyricsText;

        if (match && !firstVisible) firstVisible = block;
    });

    
    indexLinks.forEach(link => {
        const targetId = link.getAttribute('href').slice(1);
        const targetBlock = document.getElementById(targetId)?.closest('.song-block');
        link.parentElement.style.display = (targetBlock && targetBlock.style.display !== 'none') ? 'list-item' : 'none';
    });

    window.firstMatch = firstVisible;
}

function jumpToFirst() {
    if (window.firstMatch) {
        window.firstMatch.scrollIntoView({ behavior: 'smooth' });
    }
}
                  
function handleKeyDown(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        jumpToFirst();
    }
}
</script>
""")
        out.write("</head>\n<body>\n")

        out.write("<h1>Zpěvník</h1>\n")
        out.write("""
<div id="search-container">
    <input type="text" id="searchbar" placeholder="Hledat" oninput="filterSongs()" onkeydown="handleKeyDown(event)">
    <button id="jump-btn" onclick="jumpToFirst()">↓</button>
</div>
""")

        # Index
        for category in sorted(all_songs.keys(), key=lambda x: normalize_string(x)):
            out.write(f"<h2>{category.capitalize()}</h2>\n<ul class='song-index'>\n")
            for title, _ in all_songs[category]:
                anchor = sanitize_anchor(f"{category}-{title}")
                out.write(f"<li class='index-link'><a class='index-link' href='#{anchor}'>{title}</a></li>\n")
            out.write("</ul>\n")

        out.write("<hr>")
        # Songs
        for category in sorted(all_songs.keys(), key=lambda x: normalize_string(x)):
            out.write(f"<h2>{category.capitalize()}</h2>\n")
            for title, lyrics in all_songs[category]:
                anchor = sanitize_anchor(f"{category}-{title}")
                raw_title = title
                raw_lyrics = lyrics.strip()
                out.write(f"<div class='song-block'>\n")
                out.write(f"<h3 id='{anchor}' >{title}</h3>\n")
                out.write(f"<pre>{lyrics.strip()}</pre>\n")
                out.write("</div>\n")
        out.write('<a id="up" href="#">ZPĚT NAHORU</a>')
        out.write("</body>\n</html>")
    print(f"✅ Built {OUTPUT_FILE} with {sum(len(s) for s in all_songs.values())} songs in {len(all_songs)} categories.")


if __name__ == "__main__":
    generate_html()
