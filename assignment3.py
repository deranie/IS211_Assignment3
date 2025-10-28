
import urllib.request
import argparse
import csv
import re
from collections import Counter
from datetime import datetime
import sys

IMAGE_REGEX = re.compile(r".*\.(jpg|jpeg|png|gif)$", re.IGNORECASE)
BROWSERS = {
    "Chrome": re.compile(r"Chrome/"),
    "Firefox": re.compile(r"Firefox/"),
    "Internet Explorer": re.compile(r"MSIE|Trident/"),
    "Safari": re.compile(r"Safari/"),
}


def downloadData(url):
    """Download and return file contents from URL."""
    with urllib.request.urlopen(url) as response:
        data = response.read()
    return data.decode("utf-8")


def processData(data):
    """Process CSV data and return a list of tuples."""
    reader = csv.reader(data.splitlines())
    records = []
    for line in reader:
        if len(line) < 5:
            continue
        records.append(line)
    return records


def analyzeImages(records):
    """Return total hits and percentage of image requests."""
    total = len(records)
    image_hits = sum(1 for row in records if IMAGE_REGEX.match(row[0]))
    percentage = (image_hits / total) * 100 if total > 0 else 0
    return image_hits, total, percentage


def detectBrowser(user_agent):
    """Detect browser from user agent string."""
    if "Chrome" in user_agent and "Edge" not in user_agent:
        return "Chrome"
    elif "Firefox" in user_agent:
        return "Firefox"
    elif "MSIE" in user_agent or "Trident/" in user_agent:
        return "Internet Explorer"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        return "Safari"
    else:
        return "Other"


def mostPopularBrowser(records):
    """Return the most common browser and count."""
    browser_counts = Counter()
    for row in records:
        ua = row[2]
        browser = detectBrowser(ua)
        browser_counts[browser] += 1
    return browser_counts.most_common(1)[0]


def hitsByHour(records):
    """Return dictionary of hour -> hit count."""
    hits = Counter()
    for row in records:
        try:
            dt = datetime.strptime(row[1], "%m/%d/%Y %H:%M:%S")
            hits[dt.hour] += 1
        except ValueError:
            continue
    return hits


def main():
    parser = argparse.ArgumentParser(description="Process web log file.")
    parser.add_argument("--url", required=True, help="URL to the CSV file")
    parser.add_argument("--extra", action="store_true", help="Show hourly hits")
    args = parser.parse_args()

    try:
        data = downloadData(args.url)
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

    records = processData(data)

    image_hits, total, percent = analyzeImages(records)
    print(f"Image requests account for {percent:.1f}% of all requests "
          f"({image_hits}/{total})")

    browser, count = mostPopularBrowser(records)
    print(f"Most popular browser: {browser} ({count} hits)")

    if args.extra:
        hourly_hits = hitsByHour(records)
        for hour, count in sorted(hourly_hits.items(), key=lambda x: x[1], reverse=True):
            print(f"Hour {hour:02d} has {count} hits")


if __name__ == "__main__":
    main()
