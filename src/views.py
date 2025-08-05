"""
Routes and views for the flask application.
"""
from pathlib import Path
from uuid import uuid4
from datetime import datetime as dt
from flask import Flask, jsonify, render_template, request
import multiprocessing
import webview
from datetime import datetime

# from process import Process
from extract_tags import text_extraction
import os

# from moviepy.editor import *

app = Flask(__name__)
path = ""
multiprocessing.freeze_support()


@app.route("/api_status")
def start():
    return "Media Tracer WEB API & Running !! -- "


@app.route("/")
def index():
    """Renders the home page."""
    return render_template("index.html")


@app.route("/home")
def home():
    """Renders the home page."""
    return render_template("index.html")


# -------------------------------------------------------------------------------------------------------------------------
@app.route("/search_ticker")
def search_ticker():
    """Renders the Ticker Search page."""
    return render_template("search_ticker.html")


# -------------------------------------------------------------------------------------------------------------------------
@app.route("/search_ticker_local")
def search_ticker_local():
    """Renders the Ticker Search page."""
    return render_template("search_ticker_local.html")


@app.route("/display_images")
def images():
    if path != "":
        path_to_display = Path(path)

        try:
            # Extract Parentfolder
            channel_path = os.path.dirname(path_to_display)
            # Subfolder names
            channel_subfolders = [
                folder
                for folder in os.listdir(channel_path)
                if os.path.isdir(os.path.join(channel_path, folder))
            ]
            # Convert subfolder names to datetime format
            folder_dates = [
                datetime.strptime(folder, "%Y_%m_%d") for folder in channel_subfolders
            ]
            # Sort subfolder names based on latest
            sorted_dates = sorted(folder_dates, reverse=True)
            # Convert datetime to string
            latest_folder = sorted_dates[0].strftime("%Y_%m_%d")
            # Make path to display all the images
            path_to_display = channel_path + "\\" + latest_folder
        except:
            pass

        image_files = sorted(
            Path(path_to_display).glob("*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        image_urls = [str(file_path) for file_path in image_files]
        try:
            image_urls = image_urls[:50]
        except:
            pass
    else:
        image_urls = []
    return jsonify({"image_urls": image_urls})


def save_video_file(video_file):
    if not os.path.exists("./upload"):
        os.mkdir("upload")

    video_path = "./upload/" + video_file.filename
    video_file.save(video_path)

    return video_path


@app.route("/extract_text_local", methods=["POST"])
def extract_text_local():
    global target_words
    global is_capturing
    global save_directory_name
    global p1, path
    path = ""

    is_capturing = True
    try:
        source = "Uploads"

        # Get the token list from the request
        token_list = request.form["ticker"]

        ## for frontend
        target_words = token_list.replace("\r", "").split("\n")

        ## for postman requst
        # target_words = ast.literal_eval(token_list)

        # Get the video URL from the request
        video = request.files["source_video"]
        # Get the save folder name from the request
        save_directory_name = request.form["directory_name"]

        status = "Offline"

        video_path = save_video_file(video)

        # vid = extraction.read_url(stream_url)
        date = str(dt.now().date()).replace("-", "_")
        save_directory_name = save_directory_name.replace(" ", "_").replace("-", "_")
        path = f".\static\{source}\{save_directory_name}\{str(date)}"

        # extraction.read_frame(
        #     is_capturing, target_words, save_directory_name, video_path, status, "", source
        # )
        p1 = multiprocessing.Process(
            target=extraction.read_frame,
            args=(
                is_capturing,
                target_words,
                save_directory_name,
                video_path,
                status,
                "",
                source,
            ),
        )
        p1.start()

        return {"status": True, "error": "", "path": str(path)}

    except Exception as E:
        return {"status": False, "error": str(E), "path": ""}


@app.route("/extract_text", methods=["POST"])
def extract_text():
    global target_words
    global is_capturing
    global channel_name
    global p1, path
    path = ""

    is_capturing = True
    try:
        source = "Channels"

        # Get the token list from the request
        token_list = request.form["ticker"]
        target_words = token_list.replace("\r", "").split("\n")
        # Get the video URL from the request
        video_url = request.form["source_video_url"]

        # Get the save folder name from the request
        channel_name = request.form["channel"]

        # target_words = ast.literal_eval(token_list)

        stream_url, status = extraction.extract_url(
            video_url,
        )
        # vid = extraction.read_url(stream_url)
        date = str(dt.now().date()).replace("-", "_")
        channel_name = channel_name.replace(" ", "_").replace("-", "_")
        path = f".\static\{source}\{channel_name}\{str(date)}"
        # extraction.read_frame(
        #     is_capturing,
        #     target_words,
        #     channel_name,
        #     stream_url,
        #     status,
        #     video_url,
        #     source,
        # )
        p1 = multiprocessing.Process(
            target=extraction.read_frame,
            args=(
                is_capturing,
                target_words,
                channel_name,
                stream_url,
                status,
                video_url,
                source,
            ),
        )
        p1.start()

        return {"status": True, "error": "", "path": str(path)}

    except Exception as E:
        return {"status": False, "error": str(E), "path": ""}


@app.route("/stop_process", methods=["POST"])
def stop_process():
    global is_capturing, p1
    is_capturing = False
    if p1 is not None and p1.is_alive():
        p1.terminate()
        p1.join()
        p1 = None

    print("Service Killed")
    return "Video capturing stopped"


# -----------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    p1 = None
    extraction = text_extraction()

    # ## FOR EXE
    # webview.create_window("Ticker Media Search", app)
    # webview.start()

    # FOR WEB
    app.run(host="0.0.0.0", port=8099)
