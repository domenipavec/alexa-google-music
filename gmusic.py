import logging

from gmusicapi import Mobileclient

import settings

logger = logging.getLogger(__name__)

mc = Mobileclient()
logged_in = mc.login(settings.GOOGLE_USER, settings.GOOGLE_PASSWORD, settings.ANDROID_ID)


if not logged_in:
    logger.error('Could not login to google.')
    exit()


def get_playlist(playlist_id):
    playlist = [p for p in mc.get_all_user_playlist_contents() if p['id'] == playlist_id][0]

    return [s['trackId'] for s in playlist['tracks']]


def get_playlists():
    return {p['name'].lower(): p['id'] for p in mc.get_all_playlists()}


def get_stream_url(song_id):
    return mc.get_stream_url(song_id)


def get_song_info(song_id):
    return mc.get_track_info(song_id)


def find_song(query):
    return mc.search(query, max_results=1)['song_hits'][0]['track']['storeId']
