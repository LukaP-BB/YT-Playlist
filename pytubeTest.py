# -*- coding: utf-8 -*-

from pytube import YouTube
import os, json
from bs4 import BeautifulSoup

def Download_Video(id, outputPath):
    try :
        yt = YouTube(f"https://www.youtube.com/watch?v={id}")
        # print(f"https://www.youtube.com/watch?v={id}")
        # downloading the highest quality audio available
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        print(f"Downloading '{stream.default_filename}' to {outputPath}")
        path = stream.download(outputPath)
        # print(f'File downloaded to {path}')
        return path
    except Exception as e :
        print(f"https://www.youtube.com/watch?v={id}")
        with open("err_log.txt", "a+") as err_log :
            err_log.write(f"\nERROR : {e}\nhttps://www.youtube.com/watch?v={id}")


def addToMediaPlayerPlaylist(path, playlist_file=None):
    with open(playlist_file, 'r+') as fp:
        soup = BeautifulSoup(fp, features="html.parser")
        original_tag = soup.body.seq
        new_tag = soup.new_tag("media", src=path)
        original_tag.append(new_tag)

    with open(playlist_file, "w") as fp :
        fp.write(str(soup.prettify()))

def Download_Playlist(final_list, music_folder, playlist_file=None) :
    titles = [(f'{video["title"]}', video["videoId"]) for video in final_list]
    # getting the list of tracks in the folder
    files = os.listdir(music_folder)
    # getting rid of file extensions (some are .mp3, others will be .webm and so on...)
    files = [os.path.splitext(file)[0] for file in files]
    # getting only the tracks that weren't downloaded yet. I like this one :D
    newTracksIDs = [title[1] for title in titles if title[0] not in files]
    i = 1
    for id in newTracksIDs :
        print(f"Downloading video {i}/{len(newTracksIDs)}")
        path = Download_Video(id, music_folder)
        if playlist_file != None :
            addToMediaPlayerPlaylist(path, playlist_file)
        i+=1



with open("DnB_Neuro.txt", "r", encoding="utf-8") as file :
    final_list = json.load(file)
music_folder = os.path.abspath("D:/Music/4K YouTube to MP3")
playlist_file = "D:/Music/Playlists/Grosse DnB.wpl"
Download_Playlist(final_list, music_folder, playlist_file=playlist_file)


# print()
# Download_Video("NGFCb9fDtzQ", music_folder)
# with open(playlist_file, 'r+') as fp:
#     soup = BeautifulSoup(fp, features="html.parser")
#     original_tag = soup.body.seq
#     new_tag = soup.new_tag("media", src="D:\\Music\\4K YouTube to MP3\\Neonlight - BassoContinuo (2020 Remaster) Diascope Music.webm")
#     original_tag.append(new_tag)
#
# with open(playlist_file, "w") as fp :
#     fp.write(str(soup.prettify()))

# print(soup.body.seq)