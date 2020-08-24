#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# script based on code samples taken from the doc
# https://developers.google.com/youtube/v3/docs
"""
Everything regarding the Youtube API interactions.
Here, we create a "playlist file" that corresponds to a given YouTube playlist

The functions are able to create and update this file, which contains all the necessary informations for further manipulations
(eg. downloading the videos or give stats on the playlist, see stats.py and download_functions.py)
"""
import os, json, sys, re
import pytube

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def create_client() :
    """Creating a youtube client and returning it. This client is the main way to interact with youtube api"""
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "auth.json"
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube

def get_pl_name(ytb, id) :
    """Gets a playlist name given a YouTube client and a playlist ID"""
    playlist_details = ytb.playlists().list(part="snippet", id=id).execute()
    try :
        pl_name = playlist_details["items"][0]["snippet"]["title"]
    except IndexError:
        print(f"Couldn't find playlist with the given ID : {id}")
        sys.exit(1)
    # returning the playlist name without problematic characters
    return re.sub("\/|\\|<|>|:|\"|\||\?|\*", "_", pl_name)

def search(final_list, ytb, Id, nextPageToken=None) :
    """takes a list of video titles and the api client (ytb), returns the filled list"""
    #stating an api request
    request = ytb.playlistItems().list(
        part="snippet",             #the informations we want to gather
        playlistId=Id,              #playlist ID
        pageToken=nextPageToken,    #50 results max by request, we read through the pages via this token
        maxResults=500,             #who knows, maybe it'll work one day
        prettyPrint=True,           #not sure if this one is usefull
        alt="json"                  #the formatting of the response
    )
    playlist_details = request.execute()
    # https://developers.google.com/youtube/v3/docs/playlistItems <-- an example response
    for video in playlist_details["items"] :
        #gathering basic infos from the initial response
        title = video["snippet"]["title"]
        videoId = video["snippet"]["resourceId"]["videoId"]
        #gathering detailed infos on the videos of the playlist
        video_details = ytb.videos().list(
            part="snippet,statistics",
            id=videoId,
            alt="json"
            ).execute()
        #strangely, video details are not available in the playlistItems method
        channel_title = video_details["items"][0]["snippet"]["channelTitle"]
        publication_date = video_details["items"][0]["snippet"]["publishedAt"]
        stats = video_details["items"][0]["statistics"]
        ID = video_details["items"][0]["id"]
        video_details = {"title" : title,
                "videoId" : ID,
                "channel_title" : channel_title,
                "publication_date" : publication_date,
                "stats" : stats
                }
        #we don't take into account the evolution of stats to avoid upadating the whole playlist everytime
        video_IDs = [video["videoId"] for video in final_list]
        if video_details["videoId"] not in video_IDs :
            print(f"{title} ////// {channel_title} ////// {stats['viewCount']}")
            final_list.append(video_details)
        else :
            # by default, playlist is ordered by newest additions. If a video is found in final_list, there is no need to search further
            return final_list
    try:
        search(final_list, ytb, Id, nextPageToken=playlist_details["nextPageToken"])
    except Exception as e: #should happen only when there is no more next page
        return final_list

def LoadOrCreate(pl_file):
    """Loads a playlist file or create it if the file doesn't exist, returns a list object filled with the playlist details"""
    try :
        with open(pl_file, "r", encoding="utf-8") as file :
            final_list = json.load(file)
    except FileNotFoundError:
        print(f"\nCreating {pl_file}\n")
        open(pl_file, 'w+').close()
        final_list = []
    except json.decoder.JSONDecodeError: #if the file is empty
        print(f"\nPlaylist file {pl_file} was empty, let's fill it\n")
        final_list = []
    return final_list

def update(playlistId):
    """Updates or creates a playlist file given a playlist ID, returns the playlist file path"""
    #creating the api client
    youtube = create_client()
    #getting the playlist name to create the according file name
    playlist_name = get_pl_name(youtube, playlistId)
    #writting to current directory and printing the path later
    pl_file = os.path.join(os.getcwd(), f"{playlist_name}.txt")
    final_list = LoadOrCreate(pl_file)
    size_before = len(final_list)
    #writting data into final_list
    search(final_list, youtube, playlistId)
    size_after = len(final_list)
    print(f"\nThere are {size_after} videos in the playlist, \
{size_after-size_before} videos have been added since last update\n")

    with open(pl_file, "w+", encoding="utf-8") as file :
        file.write(json.dumps(final_list, indent=2))
    print(f"Playlist written to {pl_file}")
    return pl_file

if __name__ == '__main__':
    id = input("Enter a YouTube playlist ID\n")
    update(id)