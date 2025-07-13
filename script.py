import xml.etree.ElementTree as ET
import feedparser
import subprocess
import datetime
import concurrent.futures
import re
import json

OPML_FILE = "youtubeSubscriptions.opml"
DAYS_BACK = 30

def parse_opml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    feeds = []

    for outline in root.iter('outline'):
        xml_url = outline.attrib.get('xmlUrl')
        if xml_url:
            feeds.append((outline.attrib.get('title', 'Unknown'), xml_url))
    return feeds

def get_duration(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--skip-download", "--print-json", url],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)
        # Exclude livestreams and past livestreams
        if info.get("is_live") or info.get("live_status") in ("live", "was_live"):
            print(f"Skipping livestream: {info.get('title')}")
            return None  # Skip
        return info.get("duration") or 0
    except Exception as e:
        print(f"Failed to get info for {url}: {e}")
        return None

def extract_videos(feed_url, days_back):
    feed = feedparser.parse(feed_url)
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
    videos = []

    for entry in feed.entries:
        try:
            pub_date = datetime.datetime(*entry.published_parsed[:6])
            if pub_date >= cutoff:
                video_url = entry.link
                title = entry.title
                channel = feed.feed.title
                videos.append({
                    'title': title,
                    'url': video_url,
                    'published': pub_date,
                    'channel': channel
                })
        except Exception:
            continue
    return videos

def main():
    print("Parsing OPML...")
    feeds = parse_opml(OPML_FILE)

    print(f"Found {len(feeds)} feeds. Fetching videos...")
    all_videos = []
    for title, feed_url in feeds:
        vids = extract_videos(feed_url, DAYS_BACK)
        all_videos.extend(vids)

    print(f"Found {len(all_videos)} videos uploaded in the last {DAYS_BACK} days.")
    
    print("Fetching durations with yt-dlp...")

    durations = {}
    count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_video = {executor.submit(get_duration, vid['url']): vid for vid in all_videos}
        for future in concurrent.futures.as_completed(future_to_video):
            count += 1
            vid = future_to_video[future]
            duration = future.result()
            if duration is None:
                continue
            ch = vid['channel']
            durations[ch] = durations.get(ch, 0) + duration
            print('yay', count)

    print("\n=== Upload Duration Summary ===")
    for ch, total_seconds in sorted(durations.items(), key=lambda x: -x[1]):
        mins, secs = divmod(total_seconds, 60)
        hrs, mins = divmod(mins, 60)
        print(f"{ch:<40} {hrs}h {mins}m {secs}s")

if __name__ == "__main__":
    main()
