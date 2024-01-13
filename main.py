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

def get_filenames(path):
    filenames = []
    print("Getting files...")
    files = dropbox_client.files_list_folder(path=f"/{path}")
    if len(files.entries) < 1:
        print("no files found")
        sys.exit()
    for file in files.entries:
        filenames.append(file.name)

    print(f"Found {len(files.entries)} files...")
    return filenames

def download_files(path, files):
    for file in files:
        print(f"Downloading audio files...")
        dropbox_client.files_download_to_file(file, f"/{path}/{file}")
    print("Done.")

def upload_file(path, file):
    print(f"Uploading text file...")
    with open(file, "rb") as f:
        data = f.read()
    dropbox_client.files_upload(data, path=f"/{path}/{file}")

def delete_file(path, file):
    print(f"Deleting audio file...")
    dropbox_client.files_delete(f"/{path}/{file}")

def transcribe_audio(file):
    print("Starting transcribe...")
    with open(file, "rb") as file:
        transcript = openai_client.audio.transcriptions.create(model = "whisper-1", file=file)
    
    out_file = file.name.split('.')[0] + ".txt"
    with open(f"{out_file}", "w") as output_file:
        output_file.write(transcript.text)
    
    return out_file



if __name__ == "__main__":

    audio_files = get_filenames(AUDIO_PATH)
    download_files(AUDIO_PATH, audio_files)

    for file in audio_files:
        out_file = transcribe_audio(file)
        upload_file(TEXT_PATH, out_file)
        delete_file(AUDIO_PATH, file)
    
    print("Done.")


