#!/usr/bin/env python3
#-*- coding:utf-8 -*-

def addToMediaPlayerPlaylist(path, playlist_file=None):
    with open(playlist_file, 'r+') as fp:
        soup = BeautifulSoup(fp, features="html.parser")
        original_tag = soup.body.seq
        new_tag = soup.new_tag("media", src=path)
        original_tag.append(new_tag)

    with open(playlist_file, "w") as fp :
        fp.write(str(soup.prettify()))

def main():
    pass

if __name__ == '__main__':
    main()