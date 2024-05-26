import sqlite3
from sqlite3 import Error
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube, Channel
import re
import argparse

def process_video(url, conn):
    yt = YouTube(url)
    print(f"Processing video: {url}")

    if not yt.caption_tracks:
        print(f"Video {url} has no captions")
        return


    lang_code = 'pt'
    if yt.caption_tracks[0].code == 'a.en':
        lang_code = 'en'
    else:
        print(f"Video {url} has captions, but not in pt or en")
        return

    processed = conn.execute("SELECT COUNT(url) FROM processed WHERE url=?", (url,))
    if processed.fetchone()[0] == 0:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(yt.video_id)
            if transcript_list:
                transcript = YouTubeTranscriptApi.get_transcript(yt.video_id, languages=[lang_code])

                for line in transcript:
                    text = re.sub(r"[\'\"!@#$&]+", '', line["text"])
                    url_time = f"{url}&t={int(line['start'])}"
                    conn.execute("INSERT INTO transcripts (title, url, description) VALUES (?, ?, ?)", (text, url_time, yt.title))

                conn.execute("INSERT INTO processed (url) VALUES (?)", (url,))
                conn.commit()
        except Error as e:
            print(f"Error processing video {url}: {e}")
    else:
        print(f"Video {url} already processed")

def main():
    parser = argparse.ArgumentParser(description='YouTube Transcript Downloader')
    parser.add_argument('channel', help='YouTube channel ID')
    parser.add_argument('--db', default='mc_transcripts.db', help='SQLite database file')
    args = parser.parse_args()

    try:
        conn = sqlite3.connect(args.db)
        print("Database connection established")

        c = Channel(f'https://www.youtube.com/channel/{args.channel}')
        for url in c.video_urls:
            process_video(url, conn)

        print("Records created successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()
