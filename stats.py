import re, json

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

if __name__ == '__main__':
    file = input("Enter a playlist file that you wanna analyse : \n")
    statistfy(file)