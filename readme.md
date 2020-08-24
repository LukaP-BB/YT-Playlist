# Youtube Playlist Titles
## An implementation of the Youtube Data API

The idea for this project is to be able to download informations regarding a given YouTube playlist and to keep trace of all the tracks within (it happens that due to copyright, some videos are deleted). As a music lover, it's always disapointing to see that some tracks got lost but have no way to find wihch ones.

To keep track of the tracks, a playlist file is created with all basics informations regarding every video. This file is a big list that can only be appended at each update, so no track are losts anymore.

First idea

Secondary functions came quite naturally : downloading the playlist and updating the local "windows media player" playlist

## Requirements

If you want to use it for yourself, you'll need a key for the YouTube api. See how to do this [here](https://developers.google.com/youtube/v3/getting-started).
Save this key in ./secrets/key.txt (make sure there is no newline at the end of the file)
Two additional libraries are required :
- BeautifulSoup
- pytube

`pip install -r requirements.txt`

## How to use it

This program can be used with one-liner command arguments as well as through a console interface.

The later is self-explanatory, let's look at the one-liners.

```
py - 3 main.py update <your playlist id> (dl)
py -3 main.py stats <your_playlist_file.txt>
```

Two positional arguments are accepted and mandatory :
- update
  - With update, you need to provide a YouTube playlist id and if you want to download this playlist (highest audio stream available, .webm format) add the "dl" argument at the end
  - stats
- With stats, you need to provide the path (absolute or relative) to a playlist file (.txt) previously created in "userdata"