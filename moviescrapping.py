# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from difflib import SequenceMatcher


# BASE_URL = "https://moviesdatamil.co/tamil-2026-movies/"
# HEADERS = {"User-Agent": "Mozilla/5.0"}


# def get_slug(movie_link):
#     path = urlparse(movie_link).path.strip("/")
#     return path.replace("-tamil-movie", "")


# def scrap_movies():
#     movies_list = []

#     response = requests.get(
#         BASE_URL,
#         headers=HEADERS,
#         timeout=15
#     )
#     response.raise_for_status()

#     soup = BeautifulSoup(response.text, "html.parser")

#     pages = soup.select("ul.pagination a")
#     last_page = max(
#         [int(p.get_text(strip=True)) for p in pages
#          if p.get_text(strip=True).isdigit()],
#         default=1
#     )

#     print("Total pages:", last_page)

#     for page_number in range(1, last_page + 1):

#         page_url = (
#             BASE_URL
#             if page_number == 1
#             else f"{BASE_URL}?page={page_number}"
#         )

#         print(f"Scraping Page {page_number}/{last_page}")

#         response = requests.get(
#             page_url,
#             headers=HEADERS,
#             timeout=15
#         )
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, "html.parser")

#         for movie in soup.select("div.f a"):

#             movie_name = movie.get_text(strip=True)
#             href = movie.get("href")

#             if not href:
#                 continue

#             movie_link = urljoin(page_url, href)
#             slug = get_slug(movie_link)

#             movies_list.append({
#                 "name": movie_name,
#                 "url": movie_link,
#                 "slug": slug,
#                 "360p": f"{BASE_URL.rsplit('/', 2)[0]}/download/{slug}-original-360p-hd/",
#                 "720p": f"{BASE_URL.rsplit('/', 2)[0]}/download/{slug}-original-720p-hd/",
#                 "1080p": f"{BASE_URL.rsplit('/', 2)[0]}/download/{slug}-original-1080p-hd/"
#             })

#     print("\n" + "=" * 60)
#     print("SCRAPING COMPLETED")
#     print("Total movies:", len(movies_list))
#     print("=" * 60)

#     return movies_list


# def search_score(search_text, movie_name):
#     search_text = search_text.lower().strip()
#     movie_name = movie_name.lower().strip()

#     if len(search_text) < 3:
#         return 0

#     if movie_name.startswith(search_text):
#         return 100

#     if search_text in movie_name:
#         return 90

#     best_score = 0

#     for word in movie_name.split():
#         if len(word) >= 3:
#             score = SequenceMatcher(
#                 None,
#                 search_text,
#                 word
#             ).ratio() * 100

#             best_score = max(best_score, score)

#     full_score = SequenceMatcher(
#         None,
#         search_text,
#         movie_name
#     ).ratio() * 100

#     return max(best_score, full_score)


# def search_movies(search_text):
#     if len(search_text.strip()) < 4:
#         return "Please enter at least 4 characters."

#     matches = []

#     for movie in scrap_movies():
#         score = search_score(
#             search_text,
#             movie["name"]
#         )

#         if score >= 70:
#             matches.append({
#                 "movie": movie,
#                 "score": score
#             })

#     matches.sort(
#         key=lambda x: x["score"],
#         reverse=True
#     )

#     if not matches:
#         return "❌ No matching movies found."

#     result = f"\n🎬 Found {len(matches)} movie(s):\n"

#     for index, item in enumerate(matches, start=1):
#         movie = item["movie"]

#         result += (
#             f"\n{index}. {movie['name']}\n"
#             f"   {movie['url']}\n"
#             f"   Match: {item['score']:.0f}%\n"
#             f"   360p: {movie['360p']}\n"
#             f"   720p: {movie['720p']}\n"
#             f"   1080p: {movie['1080p']}\n"
#             f"{'-' * 60}\n"
#         )

#     return result


# #print(search_movies("con city"))


#!/usr/bin/env python3
"""
Terminal-based class video scraper.
No Flask, no HTML templates, no while loops — single pass only.

Flow:
 1. Ask for a class name (once).
 2. Scrape ALL pages once and collect (name, link) pairs.
 3. Fuzzy match the search term against scraped names AND links.
 4. Show all matches (index, name, link).
 5. If exactly one match -> auto-select it. If multiple -> ask which index.
 6. Scrape that movie/class in full (seasons + 360/720/1080 file links).
 7. Print everything as plain text.
"""

import sys
import difflib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_URL = "https://moviesdatamil.me"

START_URL = (
    "https://moviesdatamil.me/tamil-2026-movies/"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

#FUZZY_CUTOFF = 0.95  # lower = more lenient matching
FUZZY_CUTOFF = os.environ.get("FUZZY_CUTOFF")

# ==========================================================
# SOUP HELPER
# ==========================================================

def get_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


# ==========================================================
# STEP 1: SCRAPE ALL MAIN ITEMS (ONE PASS, FOR LOOP ONLY)
# ==========================================================

def scrape_all_movies():
    """Scrape every page exactly once using a for loop. No while loop."""
    movies = []

    #print("[*] Fetching first page...")
    first_soup = get_soup(START_URL)

    total_element = first_soup.find("span", id="totalPages")
    total_pages = int(total_element.get_text(strip=True)) if total_element else 1

    #print(f"[*] Total pages detected: {total_pages}")

    for page in range(1, total_pages):
        if page == 1:
            page_soup = first_soup
            page_url = START_URL
        else:
            page_url = f"{START_URL}?page={page}"
            #print(f"[*] Fetching page {page}: {page_url}")
            page_soup = get_soup(page_url)

        for item in page_soup.select("div.f"):
            anchor = item.find("a")
            if not anchor:
                continue

            name = anchor.get_text(strip=True)
            href = anchor.get("href")
            if not href:
                continue

            link = urljoin(BASE_URL, href)
            movies.append({"name": name, "link": link})

    #print(f"[*] Scraped {len(movies)} classes total.\n")
    return movies


# ==========================================================
# STEP 2: FUZZY MATCH (name similarity + link substring)
# ==========================================================

def fuzzy_search(movies, query):
    query_l = query.lower().strip()
    matches = []

    for movie in movies:
        name_l = movie["name"].lower()
        link_l = movie["link"].lower()

        # similarity ratio against the name
        name_ratio = difflib.SequenceMatcher(None, query_l, name_l).ratio()

        # substring check against the link (as requested)
        link_hit = query_l.replace(" ", "-") in link_l or query_l in link_l

        # substring check against the name too (helps short queries)
        name_hit = query_l in name_l

        if name_hit or link_hit or name_ratio >= FUZZY_CUTOFF:
            score = max(name_ratio, 1.0 if (name_hit or link_hit) else 0.0)
            matches.append((score, movie))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in matches]


# ==========================================================
# STEP 3: DOWNLOAD-LEVEL FOLLOW LOGIC (unchanged behavior)
# ==========================================================

def get_first_server(url):
    soup = get_soup(url)
    link = soup.select_one("div.dlink a")
    if not link:
        return None
    return {
        "text": link.get_text(" ", strip=True),
        "link": urljoin(BASE_URL, link.get("href"))
    }


def get_level_3_link(url, max_depth=3):
    current_url = url
    visited = set()
    result = None

    for level in range(1, max_depth + 1):
        if current_url in visited:
            break
        visited.add(current_url)

        try:
            download = get_first_server(current_url)
        except Exception:
            break

        if not download:
            break

        result = {"level": level, "text": download["text"], "link": download["link"]}
        current_url = download["link"]

    return result


def get_files(url):
    soup = get_soup(url)
    files = []

    for folder in soup.select("div.folder"):
        anchor = folder.select_one("div.left a")
        if not anchor:
            continue

        file_name = anchor.get_text(strip=True)
        file_link = urljoin(BASE_URL, anchor.get("href"))

        size_element = folder.select_one("li:nth-of-type(2)")
        format_element = folder.select_one("li:nth-of-type(3)")

        file_size = size_element.get_text(strip=True) if size_element else ""
        file_format = format_element.get_text(strip=True) if format_element else ""

        files.append({
            "name": file_name,
            "link": file_link,
            "size": file_size,
            "format": file_format
        })

    return files


def get_quality(text):
    text = text.lower()
    if "1080" in text:
        return "1080"
    if "720" in text:
        return "720"
    if "360" in text:
        return "360"
    return None


def add_unique(array, value):
    if not value:
        return
    if value not in array:
        array.append(value)


# ==========================================================
# STEP 4: SCRAPE THE SELECTED MOVIE/CLASS
# ==========================================================

def scrape_movie(movie_name, movie_link):
    result = {
        "name": movie_name,
        "link": movie_link,
        "season": [],
        "360": [],
        "720": [],
        "1080": []
    }

    movie_soup = get_soup(movie_link)

    for sub_item in movie_soup.select("div.f"):
        sub_anchor = sub_item.find("a")
        if not sub_anchor:
            continue

        sub_name = sub_anchor.get_text(strip=True)
        sub_link = urljoin(BASE_URL, sub_anchor.get("href"))

        if "season" in sub_name.lower():
            result["season"].append({"name": sub_name, "link": sub_link})
            continue

        quality = get_quality(sub_name)

        try:
            sub_soup = get_soup(sub_link)
        except Exception:
            continue

        final_items = sub_soup.select("div.f")

        for final_item in final_items:
            final_anchor = final_item.find("a")
            if not final_anchor:
                continue

            final_name = final_anchor.get_text(strip=True)
            final_link = urljoin(BASE_URL, final_anchor.get("href"))

            final_quality = get_quality(final_name)
            if final_quality:
                quality = final_quality

            if not quality:
                continue

            try:
                files = get_files(final_link)
            except Exception:
                continue

            for file in files:
                try:
                    level_3 = get_level_3_link(file["link"], max_depth=3)
                except Exception:
                    continue

                if not level_3:
                    continue

                add_unique(result[quality], {
                    "name": file["name"],
                    "size": file["size"],
                    "format": file["format"],
                    "text": level_3["text"],
                    "link": level_3["link"]
                })

    return result


# ==========================================================
# STEP 5: TEXT OUTPUT
# ==========================================================

def build_result_text(result, index=None, total=None):
    """Build a single formatted text block for one movie result."""
    lines = []

    header = "🎬 " + result["name"]
    if index and total:
        header = f"🎬 [{index}/{total}]  {result['name']}"

    lines.append("")
    lines.append("═" * 70)
    lines.append(header)
    lines.append("")
    lines.append(f"🔗 {result['link']}")
    lines.append("═" * 70)

    if result["season"]:
        lines.append("")
        lines.append("📁 SEASONS")
        lines.append("")
        for s in result["season"]:
            lines.append(f"   📺 {s['name']}")
            lines.append(f"      ➜ {s['link']}")
            lines.append("")

    quality_emoji = {"360": "🔻", "720": "🔸", "1080": "🔷"}

    for quality in ("360", "720", "1080"):
        lines.append("")
        lines.append(f"{quality_emoji[quality]}  {quality}p")
        lines.append("")
        files = result[quality]
        if not files:
            lines.append("   ⛔ No link available")
            continue
        for f in files:
            lines.append(f"   📄 {f['name']}   ({f['size']} • {f['format']})")
            lines.append(f"      🔗 {f['link']}")
            lines.append("")

    lines.append("═" * 70)
    lines.append("")

    return "\n".join(lines)


def build_all_results_text(results):
    """Concatenate multiple movie result blocks into one single text string."""
    total = len(results)
    parts = []

    if total > 1:
        parts.append(f"\n\n✨  {total} MATCHED CLASSES — full results below  ✨\n\n")

    for i, result in enumerate(results, start=1):
        parts.append(build_result_text(result, index=i, total=total))
        if i != total:
            parts.append("\n\n" + ("🟰" * 25) + "  NEXT MATCH  " + ("🟰" * 25) + "\n\n")

    parts.append(f"\n\n✅ Done. {total} class result(s) shown above.\n\n")

    return "".join(parts)


# ==========================================================
# MAIN (single pass, no while loops)
# ==========================================================

def main(query):
    """
    Runs the full scrape -> fuzzy match -> scrape-all-matches pipeline
    for the given class name, and RETURNS one single formatted text
    string containing every matched result (instead of printing).
    """
    if not query or not query.strip():
        return "⚠️  No class name provided."

    query = query.strip()

    try:
        all_movies = scrape_all_movies()
    except Exception as e:
        return f"⚠️  Failed to scrape class list: {e}"

    matches = fuzzy_search(all_movies, query)

    if not matches:
        return f"⚠️  No matches found for '{query}'."

    # Build a summary of matches found
    summary_lines = [f"\n🔎 Found {len(matches)} match(es) for '{query}':\n"]
    for i, m in enumerate(matches, start=1):
        summary_lines.append(f"   [{i}] 🎬 {m['name']}")
        summary_lines.append(f"       🔗 {m['link']}")
        summary_lines.append("")

    # Scrape EVERY match (no user selection) and concatenate results.
    results = []
    failures = []
    for m in matches:
        try:
            result = scrape_movie(m["name"], m["link"])
            results.append(result)
        except Exception as e:
            failures.append(f"⚠️  Failed to scrape '{m['name']}': {e}")

    if not results:
        return "\n".join(summary_lines + failures + ["\n⚠️  Nothing could be scraped successfully."])

    final_text = "\n".join(summary_lines)
    if failures:
        final_text += "\n" + "\n".join(failures) + "\n"
    final_text += "\n\n" + build_all_results_text(results)

    return final_text


# output_text = main("con city")
# print(output_text)
