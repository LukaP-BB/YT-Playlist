# -*- coding: utf-8 -*-
# script based on code samples taken from the doc
# https://developers.google.com/explorer-help/guides/code_samples#python

import os, json, sys, re

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def create_client() :
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
    playlist_details = ytb.playlists().list(part="snippet", id=id).execute()
    pl_name = playlist_details["items"][0]["snippet"]["title"]
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
        print(f"{title} ////// {channel_title} ////// {stats['viewCount']}")
        tuple = {"title" : title,
                "channel_title" : channel_title,
                "publication_date" : publication_date,
                "stats" : stats
                }
        if tuple not in final_list :
            final_list.append(tuple)
    try:
        search(final_list, ytb, Id, nextPageToken=playlist_details["nextPageToken"])
    except Exception as e: #should happen only when there is no more next page
        return final_list

def update(playlistId):
    #creating the api client
    youtube = create_client()
    #getting the playlist name to create the according file name
    playlist_name = get_pl_name(youtube, playlistId)
    #writting to current directory and printing the path later
    pl_file = os.path.join(os.getcwd(), f"{playlist_name}.txt")
    try :
        with open(pl_file, "w+", encoding="utf-8") as file :
            final_list = json.load(file)
    except json.decoder.JSONDecodeError: #if the file is empty
        final_list = []

    #writting data into final_list
    search(final_list, youtube, playlistId)
    print(f"There are {len(final_list)} videos in the playlist")

    with open(pl_file, "w+", encoding="utf-8") as file :
        file.write(json.dumps(final_list, indent=2))
    print(f"Playlist written to {pl_file}")

def statistfy(p_file):
    try :
        with open(p_file, "r", encoding="utf-8") as file :
            final_list = json.load(file)
    except Exception as e :
        print(e)
        return False

    for element in final_list :
        print(f'{element["title"]} /// {element["channel_title"]}')
    #most frequent channels
    #average view count
    #view counts graphs (boxplots ?)
    #most frequent artists

def main():
    if len(sys.argv) <= 1 :
        print("""Usage :
    // python playlist_titles.py update <YOUR_PLAYLIST_ID> <YOUR_TXT_FILE>
    // python playlist_titles.py stats <YOUR_PLAYLIST_FILE>""")

    elif len(sys.argv) > 3 :
        print("""Too much arguments given, usage :
    // python playlist_titles.py update <YOUR_PLAYLIST_ID>
    // python playlist_titles.py stats <YOUR_PLAYLIST_FILE>""")

    elif sys.argv[1] == "update" :
        try :
            playlistId = sys.argv[2]
        except :
            playlistId = "PLE1Qvz_VBuk5nOiwJyRzvTvVflYS64EiV" #my personnal playlist
        #create or update the playlist file corresponding to the given playlist ID
        update(playlistId)

    elif sys.argv[1] == "stats" :
        try :
            playlist_file = sys.argv[2]
        except :
            playlist_file = "DnB_Neuro.txt" #my personnal playlist
        statistfy(playlist_file)

    else :
        print("""Invalid argument, Usage :
    // python playlist_titles.py update <YOUR_PLAYLIST_ID>
    // python playlist_titles.py stats <YOUR_PLAYLIST_FILE>""")


if __name__ == "__main__":
    main()