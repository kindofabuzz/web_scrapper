import csv
import json

import requests
from bs4 import BeautifulSoup
import time


def scrape_reddit() -> list[dict]:
    subreddits = [
        "https://reddit.com/r/Python/top",
        "https://reddit.com/r/learnpython/hot",
    ]

    all_data = []
    for url in subreddits:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0"
        }

        subreddit_name = url # split("/")[-1]
        print(f"Scraping for: {subreddit_name}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            subreddit_data = {
                "subreddit_name": subreddit_name,
                "url": url,
                "title": soup.title.string if soup.title else "No title",
                "scraped_at": time.strftime("%Y-%m-%d")
            }

            topics = []
            discussions = []
            seen_urls = set()

            for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
                text = heading.get_text(strip=True)

                if text and len(text) > 3:
                    if any(keyword in text.lower() for keyword in
                           ["python", "coding", "programming", "noob",
                           "backend"]):
                        topics.append({
                            "title": text,
                            "type": "python_topics"
                        })

            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]

                if (text and len(text) > 1 and "/comments" in href and
                        href not in seen_urls):
                    seen_urls.add(href)

                    discussions.append({
                        "title": text[:100] + "... " if len(text) > 100
                        else text,
                        "url": href,
                        "type": "discussions"
                    })

            # Add all collected data to the result
            subreddit_data["python_topics"] = topics
            subreddit_data["discussions"] = discussions
            all_data.append(subreddit_data)
            time.sleep(3)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return all_data


def saved_scraped_data(data, filename_json="python_topics.json",
                       filename_csv="python_topics.csv"):
    if not data:
        print(f"No data")
        return

    python_data = [d for d in data if d.get("python_topics")]

    try:
        with open(filename_json, "w", encoding="utf-8") as file:
            json.dump(python_data, file, indent=4)
            print(f"Python Topics saved: {filename_json}")

        with open(filename_csv, "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Subreddit", "Type", "Title", "Url", "Scraped_at"])

            for subreddit_data in python_data:
                subreddit = subreddit_data["subreddit_name"]
                scraped_at = subreddit_data["scraped_at"]

                for topic in subreddit_data.get("python_topics", []):
                    writer.writerow([subreddit, topic["type"], topic["title"], "", scraped_at])
                for discussion in subreddit_data.get("discussions", []):
                    writer.writerow([subreddit, discussion["type"], discussion["title"], discussion["url"], scraped_at])
            print(f"Python topics saved to CSV file: {filename_csv}")

    except Exception as e:
        print("Error while saving data:", e)


# Main -> execute code above
def main():
    # global subreddit_data, silly_topics_count, silly_discussions_count
    data = scrape_reddit()

    if data:
        print("It's working!!")
        total_topics = 0
        total_discussions = 0

        for subreddit_data in data:
            topics_count = len(subreddit_data.get("python_topics", []))
            discussions_count = len(subreddit_data.get("discussions", []))

            total_topics += topics_count
            total_discussions += discussions_count

            print(f"\nSubreddit: {subreddit_data['subreddit_name']}:")
            print(f"  - {topics_count} Python Topics")
            print(f"  - {discussions_count} Discussions")

        print(f"\nTotal across all subreddits: {total_topics} Topics, {total_discussions} Discussions")

        saved_scraped_data(data)
    else:
        print("There is no data returned!")


if __name__ == '__main__':
    main()
