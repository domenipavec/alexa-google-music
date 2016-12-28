import logging
import random

import gmusic
import settings
import user_state

logger = logging.getLogger()
logger.setLevel(settings.LOGGING_LEVEL)


def get_slot_value(intent, slot):
    if slot in intent['slots']:
        if 'value' in intent['slots'][slot]:
            return intent['slots'][slot]['value']
    return ''


def build_response(speech, *directives):
    response = {}

    if speech:
        response['outputSpeech'] = {
            'type': 'PlainText',
            'text': speech,
        }

    if directives:
        response['directives'] = directives

    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response': response,
    }


def play_directive(state, previous_token=None, offset=None, next_song=False):
    if next_song:
        song_id = state['songs'][int(state['current'] + 1)]
    else:
        song_id = state['songs'][int(state['current'])]

    play_behavior = 'REPLACE_ALL'

    stream = {
        'url': gmusic.get_stream_url(song_id),
        'token': song_id,
        'offsetInMilliseconds': 0,
    }

    if offset is not None:
        stream['offsetInMilliseconds'] = offset

    if previous_token:
        play_behavior = 'ENQUEUE'
        stream['expectedPreviousToken'] = previous_token

    return {
        'type': 'AudioPlayer.Play',
        'playBehavior': play_behavior,
        'audioItem': {
            'stream': stream,
        }
    }


def stop_directive():
    return {
        'type': 'AudioPlayer.Stop'
    }


def play_playlist_action(intent, state):
    if get_slot_value(intent, 'object.type') != 'Playlist':
        return build_response('Unknown object type')

    playlist = get_slot_value(intent, 'object.name').lower()
    if not playlist:
        return build_response('You have to specify playlist name')

    playlists = gmusic.get_playlists()
    if playlist not in playlists:
        return build_response('Could not find playlist ' + playlist)

    songs = gmusic.get_playlist(playlists[playlist])
    if get_slot_value(intent, 'mode.name') == 'shuffle':
        random.shuffle(songs)

    state['songs'] = songs
    state['current'] = 0

    return build_response('Playing playlist ' + playlist, play_directive(state))


def play_resume(event, state):
    if 'context' in event and 'AudioPlayer' in event['context']:
        return build_response('', play_directive(state, offset=event['context']['AudioPlayer']['offsetInMilliseconds']))
    return build_response('', play_directive(state))


def play_previous(intent, state):
    if state['current'] == 0:
        return build_response('This is the first song in playlist')

    state['current'] -= 1

    return build_response('', play_directive(state))


def play_next(intent, state):
    if state['current'] >= len(state['songs']) - 1:
        return build_response('This is the last song in playlist')

    state['current'] += 1

    return build_response('', play_directive(state))


def playback_nearly_finished(event, state):
    previous_token = state['songs'][int(state['current'])]

    if state['current'] >= len(state['songs']) - 1:
        return build_response('')

    return build_response('', play_directive(state, previous_token, next_song=True))


def playback_started(event, state):
    state['current'] = state['songs'].index(event['request']['token'])
    return build_response('')


def intent_handler(event, state):
    intent = event['request']['intent']

    if intent['name'] == "SayHiIntent":
        return build_response("Hi")
    elif intent['name'] == "AMAZON.PlaybackAction<object@MusicCreativeWork>":
        return build_response("This is not supported yet")
    elif intent['name'] == "AMAZON.PlaybackAction<object@MusicPlaylist>":
        return play_playlist_action(intent, state)
    elif intent['name'] == "AMAZON.PauseIntent" or intent['name'] == "AMAZON.StopIntent":
        return build_response('', stop_directive())
    elif intent['name'] == "AMAZON.ResumeIntent":
        return play_resume(event, state)
    elif intent['name'] == "AMAZON.NextIntent":
        return play_next(intent, state)
    elif intent['name'] == "AMAZON.PreviousIntent":
        return play_previous(intent, state)
    else:
        return build_response("Got unexpected intent")


def lambda_handler(event, context):
    logger.info('got event {}'.format(event))

    if 'session' in event:
        user = event['session']['user']
        application = event['session']['application']
    elif 'context' in event and 'System' in event['context']:
        user = event['context']['System']['user']
        application = event['context']['System']['application']
    else:
        raise Exception("Invalid event")

    if application['applicationId'] != settings.ALEXA_APPLICATION_ID:
        raise ValueError("Invalid Application ID")

    state = user_state.get(user['userId'])
    logger.info('got state {}'.format(state))

    result = build_response('')

    if event['request']['type'] == "IntentRequest":
        result = intent_handler(event, state)
    elif event['request']['type'] == 'AudioPlayer.PlaybackNearlyFinished':
        result = playback_nearly_finished(event, state)
    elif event['request']['type'] == 'AudioPlayer.PlaybackStarted':
        result = playback_started(event, state)

    user_state.save(user['userId'], state)

    return result
