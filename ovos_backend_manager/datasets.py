import json
import os

from ovos_local_backend.database.settings import DeviceDatabase
from ovos_local_backend.database.utterances import JsonUtteranceDatabase
from ovos_local_backend.database.wakewords import JsonWakeWordDatabase
from pywebio.input import actions
from pywebio.output import put_text, put_code, use_scope, put_markdown


def ww_select(back_handler=None, uuid=None):
    buttons = []
    db = JsonWakeWordDatabase()
    if not len(db):
        with use_scope("datasets", clear=True):
            put_text("No wake words uploaded yet!")
        datasets_menu(back_handler=back_handler)
        return

    for m in db:
        if uuid is not None and m["uuid"] != uuid:
            continue
        name = f"{m['wakeword_id']}-{m['transcription']}"
        buttons.append({'label': name, 'value': m['wakeword_id']})

    if len(buttons) == 0:
        with use_scope("datasets", clear=True):
            put_text("No wake words uploaded from this device yet!")
        opt = "main"
    else:
        if back_handler:
            buttons.insert(0, {'label': '<- Go Back', 'value': "main"})
        opt = actions(label="Select a WakeWord recording",
                      buttons=buttons)
    if opt == "main":
        ww_menu(back_handler=back_handler)
        return
    # id == db_position + 1
    with use_scope("datasets", clear=True):
        put_code(json.dumps(db[opt - 1], indent=4), "json")
    ww_select(back_handler=back_handler)


def utt_select(back_handler=None, uuid=None):
    buttons = []
    db = JsonUtteranceDatabase()
    if not len(db):
        with use_scope("datasets", clear=True):
            put_text("No utterances uploaded yet!")
        datasets_menu(back_handler=back_handler)
        return

    for m in db:
        if uuid is not None and m["uuid"] != uuid:
            continue
        name = f"{m['utterance_id']}-{m['transcription']}"
        buttons.append({'label': name, 'value': m['utterance_id']})

    if len(buttons) == 0:
        with use_scope("datasets", clear=True):
            put_text("No utterances uploaded from this device yet!")
        opt = "main"
    else:
        if back_handler:
            buttons.insert(0, {'label': '<- Go Back', 'value': "main"})
        opt = actions(label="Select a Utterance recording",
                      buttons=buttons)
    if opt == "main":
        utt_menu(back_handler=back_handler)
        return

    # id == db_position + 1
    with use_scope("datasets", clear=True):
        put_code(json.dumps(db[opt - 1], indent=4), "json")
    utt_select(back_handler=back_handler)


def device_select(back_handler=None, ww=True):
    devices = {uuid: f"{device['name']}@{device['device_location']}"
               for uuid, device in DeviceDatabase().items()}
    buttons = [{'label': "All Devices", 'value': "all"}] + \
              [{'label': d, 'value': uuid} for uuid, d in devices.items()]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    if devices:
        uuid = actions(label="What device would you like to inspect?",
                       buttons=buttons)
        if uuid == "main":
            datasets_menu(back_handler=back_handler)
            return
        else:
            if uuid == "all":
                uuid = None
            if ww:
                ww_select(uuid=uuid, back_handler=back_handler)
            else:
                utt_select(uuid=uuid, back_handler=back_handler)
    else:
        with use_scope("datasets", clear=True):
            put_text("No devices paired yet!")
        if ww:
            ww_menu(back_handler=back_handler)
        else:
            utt_menu(back_handler=back_handler)


def ww_menu(back_handler=None):
    buttons = [{'label': 'Inspect Wake Words', 'value': "ww"},
               {'label': 'Delete wake words database', 'value': "delete_ww"}]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)
    if opt == "ww":
        device_select(back_handler=back_handler, ww=True)
    if opt == "delete_ww":
        with use_scope("datasets", clear=True):
            put_markdown("""Are you sure you want to delete the wake word database?
            **this can not be undone**, proceed with caution!
            **ALL** wake word recordings will be **lost**""")
        opt = actions(label="Delete wake words database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:
            # TODO - also remove files from path
            os.remove(JsonWakeWordDatabase().db.path)
            with use_scope("datasets", clear=True):
                put_text("wake word database deleted!")
        datasets_menu(back_handler=back_handler)
        return
    if opt == "main":
        with use_scope("datasets", clear=True):
            datasets_menu(back_handler=back_handler)
        return
    ww_menu(back_handler=back_handler)


def utt_menu(back_handler=None):
    buttons = [{'label': 'Inspect Recordings', 'value': "utt"},
               {'label': 'Delete utterances database', 'value': "delete_utt"}]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)
    if opt == "utt":
        device_select(back_handler=back_handler, ww=False)
    if opt == "delete_utt":
        with use_scope("datasets", clear=True):
            put_markdown("""Are you sure you want to delete the utterances database?
                        **this can not be undone**, proceed with caution!
                        **ALL** utterance recordings will be **lost**""")
        opt = actions(label="Delete utterances database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:
            # TODO - also remove files from path
            os.remove(JsonUtteranceDatabase().db.path)
            with use_scope("datasets", clear=True):
                put_text("utterance database deleted!")
        datasets_menu(back_handler=back_handler)
        return
    if opt == "main":
        with use_scope("datasets", clear=True):
            datasets_menu(back_handler=back_handler)
        return

    utt_menu(back_handler=back_handler)


def datasets_menu(back_handler=None):
    buttons = [{'label': 'Wake Words', 'value': "ww"},
               {'label': 'Utterance Recordings', 'value': "utt"}
               ]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)

    if opt == "utt":
        utt_menu(back_handler=back_handler)
    if opt == "ww":
        ww_menu(back_handler=back_handler)
    if opt == "main":
        with use_scope("datasets", clear=True):
            back_handler()
        return
    datasets_menu(back_handler=back_handler)
