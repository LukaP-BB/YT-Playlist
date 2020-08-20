# -*- coding: utf-8 -*-
# script based on code samples taken from the doc
# https://developers.google.com/youtube/v3/docs

import os, json, sys, re
import pytube

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def Download_Playlist(playlist, dl_folder):
    youtube_address = "https://www.youtube.com/watch?v="



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

def update(playlistId):
    #creating the api client
    youtube = create_client()
    #getting the playlist name to create the according file name
    playlist_name = get_pl_name(youtube, playlistId)
    #writting to current directory and printing the path later
    pl_file = os.path.join(os.getcwd(), f"{playlist_name}.txt")
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

    size_before = len(final_list)
    #writting data into final_list
    search(final_list, youtube, playlistId)
    size_after = len(final_list)
    print(f"\nThere are {size_after} videos in the playlist, \
{size_after-size_before} videos have been added since last update\n")

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
    freq_channels = {}
    artists = {}
    missing = []
    sum_views = 0
    min_views = 1000000000000
    max_views = 0
    #lets loop over the videos in the playlist and gather some stats
    for element in final_list :
        #extracting the artists from the titles (luckily the titles nomenclature is pretty consistent)
        v_title = re.search("(.*)(( [-–] )|( -- ))(.*)", element["title"])
        if v_title :
            artist = v_title.group(1)
            #splitting the featurings
            l_artists = re.split(" feat. | feat | ft. | & | and ", artist)
        else :
            l_artists = re.split(" - Topic", element["channel_title"])

        for artist in l_artists :
            if artist not in artists and artist != "":
                artists[artist] = 1
            elif artist != "" :
                artists[artist] += 1

        #counting the views
        views = int(element["stats"]["viewCount"])
        sum_views += views
        if views > max_views :
            max_views = views
            max_views_vid = element["title"]
        if views < min_views :
            min_views = views
            min_views_vid = element["title"]

        #counting the channels
        channel_title = element["channel_title"]
        if channel_title not in freq_channels :
            freq_channels[channel_title] = 1
        else :
            freq_channels[channel_title] +=1

    # sorting the artists by the most amount of videos in the playlist
    artists = sorted(artists.items(), key=lambda item : item[1], reverse=True)
    i = 0
    print("\n---------------------------------------\n\nMost frequent artists in the playlist : \n")
    # printing all artists appearing more than 2 times in the playlist
    while artists[i][1] >= 3 :
        print(f"{str(artists[i][1]).rjust(5)} /// {artists[i][0]}")
        i += 1

    avg_views = sum_views/len(final_list)
    print(f"\nAverage view count = {round(avg_views, 1)}\n\
    Min view count = {str(min_views).ljust(9)}| {min_views_vid}\n\
    Max view count = {str(max_views).ljust(9)}| {max_views_vid}\n")
    freq_channels = sorted(freq_channels.items(), key=lambda item : item[1], reverse=True)
    a = True
    i = 0
    print("Channels appearing more than once : ")
    # plot_channels(freq_channels)
    while freq_channels[i][1] > 1 and i < len(freq_channels)-1 :
        print(f"{str(freq_channels[i][1]).rjust(5)} /// {freq_channels[i][0]}")
        i += 1

    print(f"There are {len(final_list)} tracks in the playlist")

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