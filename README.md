Count total video length for all channels in an OPML file (excluding livestreams) for some number of days. Use if you want to know which channels spam the most.

## Setup

`pip install feedparser`

Make sure [yt-dlp](https://github.com/yt-dlp/yt-dlp) is installed

## Instructions

- Use [userscript](https://greasyfork.org/en/scripts/418574-export-youtube-subscriptions-to-rss-opml) to export your subscriptions to an OPML file, put it in the directory
- Change `DAYS_BACK` to desired
- Run the file

Code 100% written by ChatGPT

May or may not have +-1 day difference (timezones are weird?? idk). Use for approximation only
