import zipfile
from os import makedirs, walk
from os.path import dirname, isfile, isdir
from shutil import copy
from tempfile import gettempdir

import requests

LANGS = ["en-us", "es-es", "de-de", "fr-fr", "it-it", "pt-pt"]
BRANCH = "dev"

SKILLS_LIST = f"{dirname(dirname(__file__))}/skill_repos.txt"
SKILLS_FOLDER = f"{gettempdir()}/skills"

makedirs(SKILLS_FOLDER, exist_ok=True)

with open(SKILLS_LIST) as f:
    skill_urls = [f for f in f.read().split("\n") if f.strip()]

for url in skill_urls:
    repo = url.split("/")[-1].lower()
    author = url.split("/")[-2].lower()
    skill_id = f"{repo}.{author}".lower()
    zip_url = f"{url}/archive/refs/heads/dev.zip"

    filename = skill_id + ".zip"
    zip_path = f"{SKILLS_FOLDER}/{filename}"

    # download repo
    if not isfile(zip_path):
        r = requests.get(zip_url)
        if r.status_code != 200:
            print("error downloading", zip_url)
            continue
        with open(zip_path, "wb") as f:
            f.write(r.content)
            print("downloaded", zip_url)

    # extract .zip file
    author_folder = f"{SKILLS_FOLDER}/{author}"
    makedirs(author_folder, exist_ok=True)
    skill_path = f"{author_folder}/{repo}-dev"
    if not isdir(skill_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(author_folder)

    # scan dialog files and move to DIALOGS_FOLDER
    for LANG in LANGS:
        DIALOGS_FOLDER = f"{dirname(dirname(__file__))}/dialog_files/{LANG}"
        makedirs(DIALOGS_FOLDER, exist_ok=True)
        dialogs = []
        for root, folders, files in walk(skill_path):
            if "/unittests/" in root or "/integrationtests/" in root:
                continue
            if root.endswith(f"/{LANG}") or f"/{LANG}/" in root:
                dialogs += [f"{root}/{f}" for f in files if f.endswith(".dialog")]
        print(skill_id, LANG, dialogs)
        if dialogs:
            dialog_folder = f"{DIALOGS_FOLDER}/{skill_id}"
            makedirs(dialog_folder, exist_ok=True)
            for dialog in dialogs:
                dst = f"{dialog_folder}/{dialog.split('/')[-1]}"
                if not isfile(dst):
                    copy(dialog, dst)
