from openai import OpenAI
import dropbox
import os, sys, json
from rich import print

def get_config():
    required_vars = ["DROPBOX_APP_KEY", "DROPBOX_APP_SECRET", "DROPBOX_REFRESH_TOKEN", "OPENAI_API_KEY"]
    config = {}

    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        sys.exit(f"Error: Missing environment variables: {', '.join(missing_vars)}")

    for var in required_vars:
        config[var.lower()] = os.environ[var]

    return config

config = get_config()
openai_client = OpenAI()
dropbox_client = dropbox.Dropbox(app_key=
                                 config['dropbox_app_key'],
                                 app_secret=config['dropbox_app_secret'],
                                 oauth2_refresh_token=config['dropbox_refresh_token']
)
AUDIO_PATH = "voice-memos"
TEXT_PATH = "text-transcripts"

def get_filename(path):
    print("Getting files...")
    files = dropbox_client.files_list_folder(path=f"/{path}")
    if len(files.entries) < 1:
        print("no files found")
        sys.exit()
    filename = files.entries[0].name
    print(f"found: {filename}")
    return filename

def download_file(path, file):
    print(f"Downloading file: {file}...")
    dropbox_client.files_download_to_file(file, f"/{path}/{file}")
    print("Done.")

def upload_file(path, file):
    print(f"Uploading file: {file}...")
    with open(file, "rb") as f:
        data = f.read()
    dropbox_client.files_upload(data, path=f"/{path}/{file}")

def delete_file(path, file):
    print(f"Deleting file: {file}...")
    dropbox_client.files_delete(f"/{path}/{file}")
    print("Done.")

def transcribe_audio(file):
    print("Starting transcribe...")
    with open(file, "rb") as file:
        transcript = openai_client.audio.transcriptions.create(model = "whisper-1", file=file)
    
    out_file = file.name.split('.')[0] + ".txt"
    print(f"writing to {out_file}...")
    with open(f"{out_file}", "w") as output_file:
        output_file.write(transcript.text)
    
    return out_file



if __name__ == "__main__":

    audio_file = get_filename(AUDIO_PATH)
    download_file(AUDIO_PATH, audio_file)
    out_file = transcribe_audio(audio_file)
    upload_file(TEXT_PATH, out_file)
    delete_file(AUDIO_PATH, audio_file)


