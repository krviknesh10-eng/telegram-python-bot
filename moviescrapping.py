import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from difflib import SequenceMatcher


BASE_URL = "https://moviesdatamil.co/tamil-2026-movies/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_slug(movie_link):
    path = urlparse(movie_link).path.strip("/")
    return path.replace("-tamil-movie", "")


def scrap_movies():
    movies_list = []

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pages = soup.select("ul.pagination a")
    last_page = max(
        [int(p.get_text(strip=True)) for p in pages
         if p.get_text(strip=True).isdigit()],
        default=1
    )

    print("Total pages:", last_page)

    for page_number in range(1, last_page + 1):

        page_url = (
            BASE_URL
            if page_number == 1
            else f"{BASE_URL}?page={page_number}"
        )

        print(f"Scraping Page {page_number}/{last_page}")

        response = requests.get(
            page_url,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for movie in soup.select("div.f a"):

            movie_name = movie.get_text(strip=True)
            href = movie.get("href")

            if not href:
                continue

            movie_link = urljoin(page_url, href)
            slug = get_slug(movie_link)

            movies_list.append({
                "name": movie_name,
                "url": movie_link,
                "slug": slug,
                "360p": f"{BASE_URL.rsplit('/', 2)[0]}/download/{slug}-original-360p-hd/",
                "720p": f"{BASE_URL.rsplit('/', 2)[0]}/download/{slug}-original-720p-hd/",
                "1080p": f"{BASE_URL.rsplit('/', 2)[0]}/download/{slug}-original-1080p-hd/"
            })

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETED")
    print("Total movies:", len(movies_list))
    print("=" * 60)

    return movies_list


def search_score(search_text, movie_name):
    search_text = search_text.lower().strip()
    movie_name = movie_name.lower().strip()

    if len(search_text) < 3:
        return 0

    if movie_name.startswith(search_text):
        return 100

    if search_text in movie_name:
        return 90

    best_score = 0

    for word in movie_name.split():
        if len(word) >= 3:
            score = SequenceMatcher(
                None,
                search_text,
                word
            ).ratio() * 100

            best_score = max(best_score, score)

    full_score = SequenceMatcher(
        None,
        search_text,
        movie_name
    ).ratio() * 100

    return max(best_score, full_score)


def search_movies(search_text):
    if len(search_text.strip()) < 4:
        return "Please enter at least 4 characters."

    matches = []

    for movie in scrap_movies():
        score = search_score(
            search_text,
            movie["name"]
        )

        if score >= 70:
            matches.append({
                "movie": movie,
                "score": score
            })

    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not matches:
        return "❌ No matching movies found."

    result = f"\n🎬 Found {len(matches)} movie(s):\n"

    for index, item in enumerate(matches, start=1):
        movie = item["movie"]

        result += (
            f"\n{index}. {movie['name']}\n"
            f"   {movie['url']}\n"
            f"   Match: {item['score']:.0f}%\n"
            f"   360p: {movie['360p']}\n"
            f"   720p: {movie['720p']}\n"
            f"   1080p: {movie['1080p']}\n"
            f"{'-' * 60}\n"
        )

    return result


#print(search_movies("con city"))
