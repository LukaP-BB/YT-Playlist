#!/usr/bin/env python3
#-*- coding:utf-8 -*-
"""
Main program implementing the high level interactions with the user
    - main() function provides a way to interact with arguments only
    - mainLoop() helps the user a bit more
"""
import update as upd
import download_functions as dlf
import stats, sys, os, json

welcome_txt = """
YT-Playlist - A command-line untility to download YouTube playlists :
You can either use this interface or skip it by using arguments. To know more about it, enter [0].

Select your action :
[0] : some help on the command line arguments
[1] : update a playlist or download a new one
[2] : get some stats on a given playlist
[3] : quit
"""

def configPaths():
    """When first launching the program, creates "userdata" and a config file, then load this file on launch"""
    try :
        with open("userdata/config.json", "r") as config_file :
            config = json.load(config_file)
            return config
    except FileNotFoundError :
        if not os.path.exists("userdata") :
            os.makedirs("userdata")
        choice = input("""
First time launching the program ? You can either setup the folders where every informations will be stored or skip this step for a quick and dirty setup.
[1] Quick and dirty (Everything will be downloaded to ./userdata)
[2] Full setup
""")
    except json.decoder.JSONDecodeError:
        choice = input("""
Your config file is empty, let's fill it with the proper informations.
[1] Quick and dirty (Everything will be downloaded to ./userdata)
[2] Full setup
""")

    if choice == "1" :
        config = {
            "music_folder" : "userdata",
            "playlist_folder" : "userdata"
        }
        with open("userdata/config.json", "w+") as config_file :
            json.dump(config, config_file)
    elif choice == "2" :
        music_folder = input("Enter the absolute path to the folder where you want your music downloaded.\n")
        playlist_folder = input("Enter the absolute path to the folder where your windows media player playlists are stored. Press enter if you wont use this feature")
        if playlist_folder == "" :
            playlist_folder = "userdata"
        config = {
            "music_folder" : music_folder,
            "playlist_folder" : playlist_folder
        }
        with open("userdata/config.json", "w+") as config_file :
            json.dump(config, config_file)
    else :
        print("Enter a valid value.\n")
        configPaths()

    print("Config file written to ./userdata\n")
    return config


def help():
    #a help message
    help_message = """
How to use this program with arguments :
py - 3 main.py update <your playlist id> (dl)
py -3 main.py stats <your_playlist_file.txt>

Two positional arguments are accepted and mandatory :
    update
        With update, you need to provide a YouTube playlist id
        and if you want to download this playlist (highest audio stream available, .webm format)
        add the "dl" argument at the end
    stats
        With stats, you need to provide the path (absolute or relative) to a playlist file (.txt) previously created in "userdata"

You can also simply use :
py -3 main.py
and let the program guide you through the process
"""
    print(help_message)

def mainLoop(config, repeat=False):
    """Loop for the friendly interface with the program"""
    if repeat :
        choice = input("Please enter a valid option\n")
    else :
        choice = input(welcome_txt)

    if choice not in ["0","1","2","3"] :
        mainLoop(config, repeat=True)
    elif choice == "0" :
        help()
    elif choice == "1" :
        ID = input("Enter your playlist ID\n")
        pl_file = upd.update(ID)
        downloadB = input("Download this playlist ? [y/n]\n")
        if downloadB.lower() == "y" :
            music_folder = config["music_folder"]
            with open(pl_file, "r") as playlist_file :
                final_list = json.load(playlist_file)
            dlf.Download_Playlist(final_list, music_folder)
    elif choice == "2" :
        playlist_file = input("Enter the name of your playlist file for which you want stats\n")
        stats.statistfy(f"userdata/{playlist_file}")
    elif choice == "3" :
        print("Goodbye !")
        sys.exit(0)

def main():
    """Command line interface"""
    config = configPaths()
    if len(sys.argv) <= 1 :
        mainLoop(config)

    elif len(sys.argv) > 4 :
        print("Too much arguments given")
        help()

    elif sys.argv[1] == "update" :
        try :
            playlistId = sys.argv[2]
        except :
            playlistId = "PLE1Qvz_VBuk5nOiwJyRzvTvVflYS64EiV" #my personnal playlist
        #create or update the playlist file corresponding to the given playlist ID
        pl_file = upd.update(playlistId)
        music_folder = config["music_folder"]
        playlist_file = f"{config['playlist_folder']}{pl_file[:9][9:]}.wpl"
        with open(pl_file, "r", encoding="utf-8") as file :
            final_list = json.load(file)

        if len(sys.argv) > 3 :
            if sys.argv[3] ==  "dl" :
                dlf.Download_Playlist(final_list, music_folder, playlist_file=playlist_file)

    elif sys.argv[1] == "stats" :
        try :
            playlist_file = sys.argv[2]
        except :
            playlist_file = "userdata/DnB_Neuro.txt" #my personnal playlist
        stats.statistfy(playlist_file)

    else :
        print("Invalid arguments")
        help()


if __name__ == "__main__":
    main()