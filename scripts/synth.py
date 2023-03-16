import json
from os import makedirs, listdir, walk
from time import sleep
from os.path import dirname, isfile

from ovos_plugin_manager.tts import load_tts_plugin
from ovos_plugin_manager.utils.tts_cache import hash_sentence

LANGS = ["en-us", "es-es", "de-de", "fr-fr", "it-it", "pt-pt"]
VOICES_BASE = f"{dirname(dirname(__file__))}/tts_voices"
OUTPUT_BASE = f"{dirname(dirname(__file__))}/synth_data"
makedirs(OUTPUT_BASE, exist_ok=True)
makedirs(VOICES_BASE, exist_ok=True)

for LANG in LANGS:
    utts = []
    engines = {}

    DIALOGS_FOLDER = f"{dirname(dirname(__file__))}/dialog_files/{LANG}"
    VOICES_FOLDER = f"{VOICES_BASE}/{LANG}"

    for root, folders, files in walk(DIALOGS_FOLDER):
        for f in files:
            dialog = f"{root}/{f}"
            with open(dialog) as f:
                utts += [l for l in f.read().split("\n")
                         if l.strip() and not l.startswith("#")
                         and "{" not in l and "}" not in l]
    print(LANG, utts)

    for voice in listdir(VOICES_FOLDER):

        cfg = f"{VOICES_FOLDER}/{voice}"
        if not isfile(cfg):
            continue

        OUTPUT_DIR = f"{OUTPUT_BASE}/{voice.replace('.json', '')}"
        makedirs(OUTPUT_DIR, exist_ok=True)

        with open(cfg) as f:
            cfg = json.load(f)
        m = cfg.pop("module")

        if m in engines:
            engine = engines[m]
        else:
            try:
                engine = engines[m] = load_tts_plugin(m)(config=cfg)
            except:
                print("failed to load engine", m)
                continue

        for utt in utts:
            name = hash_sentence(utt)
            wav_file = f"{OUTPUT_DIR}/{name}.{engine.audio_ext}"
            if isfile(wav_file):  # handle converted mp3 files
                continue
            print(wav_file)
            # print(name)
            kwargs = {}
            if "speaker" in cfg:
                kwargs["speaker"] = cfg["speaker"]
            if "voice" in cfg:
                kwargs["voice"] = cfg["voice"]
            try:
                engine.get_tts(utt, wav_file, **kwargs)
                if "server" in voice:
                    sleep(1)  # do not overload public servers
            except:
                print("FAILED to synth", utt)