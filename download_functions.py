#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from pytube import YouTube
import os, json, re
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
        print(f"Couldn't download https://www.youtube.com/watch?v={id}")
        with open("userdata/err_log.txt", "a+") as err_log :
            err_log.write(f"\nERROR : {e}\nhttps://www.youtube.com/watch?v={id}")
        return False


def addToMediaPlayerPlaylist(path, playlist_file=None):
    with open(playlist_file, 'r+') as fp:
        soup = BeautifulSoup(fp, features="html.parser")
        original_tag = soup.body.seq
        new_tag = soup.new_tag("media", src=path)
        original_tag.append(new_tag)

    with open(playlist_file, "w") as fp :
        fp.write(str(soup.prettify()))

def regexReplace(matchobj):
    # print(matchobj.group(0))
    if matchobj.group(0) in ["/","\\","<",">",":","\"","\|","\?","\*"] :
        return ''
    elif matchobj.group(0) == "." :
        # print("ok")
        return ''

def Download_Playlist(final_list, music_folder) :
    # creating a list of tuples (videoId, videoTitle (clean), videoTitle)
    titles = [(video["videoId"],                                                # the unique video ID that will be used for the download
                re.sub("\/|\\|<|>|:|\"|\||\?|\*|\.|'|,", "", video["title"]),   # the video title, cleaned of some characters, as given by pytube
                video["title"])                                                 # the raw video title
                for video in final_list]
    # getting the list of tracks in the folder
    files = os.listdir(music_folder)
    # getting rid of file extensions (some are .mp3, others will be .webm and so on...)
    files = [os.path.splitext(file)[0] for file in files]
    # getting only the tracks that weren't downloaded yet. I like this one :D
    newTracksIDs = [title[0] for title in titles if title[1] not in files and title[2] not in files]
    i = 1
    Fail = False
    for id in newTracksIDs :
        print(f"{i}/{len(newTracksIDs)}")
        if Download_Video(id, music_folder) == False :
            fail = True

    if len(newTracksIDs) > 0 and not Fail:
        print(f"Finished downloading your tracks in this  folder : {music_folder}")
    elif len(newTracksIDs) > 0 and Fail :
        print(f"Some downloads have failed. Trying again usually works. If not, contact me on github.")
    elif len(newTracksIDs) == 0 :
        print("All the videos have already been downloaded !")


if __name__ == '__main__':
    with open("DnB_Neuro.txt", "r", encoding="utf-8") as file :
        final_list = json.load(file)
    music_folder = os.path.abspath("D:/Music/4K YouTube to MP3")
    playlist_file = "D:/Music/Playlists/Grosse DnB.wpl"
    Download_Playlist(final_list, music_folder, playlist_file=playlist_file)
