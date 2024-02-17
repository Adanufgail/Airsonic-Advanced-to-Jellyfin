# Airsonic-to-Jellyfin

This is a tool for taking starred songs (global for all users) and playlists (per user and global) in Airsonic (probably will work in other variants) and migrating them to a specific user in Jellyfin.

This tool will look for a specific credentials file (named "credentials") which should be fairly straightforward to fillout. An example is provided.

Current Functionality:

At present, it authenticates with Airsonic, pulls all starred songs from Airsonic, can authenticate with Jellyfin, and can search for songs.

REQUIREMENTS:

- Python 3
- [thefuzz](https://github.com/seatgeek/thefuzz)
