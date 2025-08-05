import cv2
import subprocess
import pytesseract
from datetime import datetime
from threading import Thread
import os
from flask import Flask, request
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class text_extraction:
    def detect_text(self, frame, count, fps, start, target_words, channel_name, source):
        """Function To Read Frame And Extract Text From Frame"""

        # Appending Frames fro
        if count % fps == 0:
            try:
                d = pytesseract.image_to_data(
                    frame, config="--psm 6", output_type=pytesseract.Output.DICT
                )
                print(
                    "FRAMES DONE  :: ",
                    str(count),
                    "  +++  CHANNEL NAME  :: ",
                    str(channel_name),
                )
                end_time = datetime.now()
                print("Time Taken Per frame  ::  ", str(end_time - start))
                for n in range(len(d["text"])):
                    for t_text in target_words:
                        date = str(datetime.now().date()).replace("-", "_")
                        time = (
                            str(datetime.now().time())
                            .replace(":", "_")
                            .replace(".", "_")
                        )
                        if d["text"][n].upper() == t_text.upper():
                            (x, y, w, h) = (
                                d["left"][n],
                                d["top"][n],
                                d["width"][n],
                                d["height"][n],
                            )
                            conf = d["conf"][n]

                            if not os.path.exists("static"):
                                os.mkdir("static")

                            if not os.path.exists("static" + "/" + source):
                                os.mkdir("static" + "/" + source)

                            sub_path = "static" + "/" + source

                            if not os.path.exists(sub_path + "/" + channel_name):
                                os.mkdir(sub_path + "/" + channel_name)

                            if not os.path.exists(
                                sub_path + "/" + channel_name + "/" + date
                            ):
                                os.mkdir(sub_path + "/" + channel_name + "/" + date)

                            if conf > 50:
                                cv2.rectangle(
                                    frame, (x, y), (x + w, y + h), (50, 150, 100), 3
                                )
                                cv2.imwrite(
                                    f"static\{source}\{channel_name}\{date}\{t_text}_{time}.jpg",
                                    frame,
                                )

            except Exception as E:
                print(f"Error in detect_text: ", str(E))

    def read_frame(
        self,
        is_capturing,
        target_words,
        channel_name,
        stream_url,
        status,
        video_url,
        source,
    ):
        """Function To Read Video And Process Frames"""
        vid = cv2.VideoCapture(stream_url)
        count = 0
        fps = self.read_fps(vid)

        if fps == 0:
            for i in range(5):
                vid = cv2.VideoCapture(stream_url)
                fps = self.read_fps(vid)
                if fps != 0:
                    break
            if i == 4:
                print("FPS is 0, Internet is not working / unstable")
                vid.release()

        ### Checking if fps is greater than 60 ###
        if fps > 60:
            fps = 30

        if status == "Offline":
            frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
            total_seconds = frame_count / int(fps)
            hours = int(total_seconds / 3600)
            minutes = int((total_seconds % 3600) / 60)
            seconds = int(total_seconds % 60)

            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            start1 = datetime.now()

        while is_capturing:
            try:
                # Read the next frame
                ret, frame = vid.read()
                count += 1
                # Check if frame reading was successful
                if not ret:
                    try:
                        if status != "Offline":
                            vid = cv2.VideoCapture(stream_url)
                            if vid.read()[0] == False:
                                try:
                                    stream_url, _ = self.extract_url(video_url)
                                    vid = cv2.VideoCapture(stream_url)
                                except Exception as e:
                                    print(
                                        "::   Error in the Live Stream (Link Expired/Internet Disconected), Extracting M3U8 Link again for the Live Stream   ::"
                                    )
                                    print(f"::   Error: {e}   ::")

                        else:
                            end1 = datetime.now()
                            is_capturing = False
                            time.sleep(2)
                            print(f"Video Duration  ::  {time_str}")
                            print(f"Total Time Taken  ::  {str(end1-start1)}")
                            print("Video Completed")
                            pass
                    except Exception as e:
                        print(
                            f"::   Error in Capturing Frame, trying again   ::   Error {e}"
                        )
                        pass

                if is_capturing == False:
                    capture.release()
                    capture = None
                    break

                start = datetime.now()

                # self.detect_text(frame, count, fps, start, target_words, channel_name, source)
                t1 = Thread(
                    target=self.detect_text,
                    args=(frame, count, fps, start, target_words, channel_name, source),
                )
                t1.start()
            except:
                pass
        vid.release()

    def extract_url(self, youtube_url):
        """Function To Extract m3u8 url to read live feed in python"""
        status = "Live"
        if "&ab_channel" in youtube_url:
            url = youtube_url.split("&ab_channel")
            youtube_url = url[0]
        command = f"yt-dlp -g {youtube_url}"
        output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
        if output.split(".")[-1] != "m3u8":
            output = output.split("\n")[0]
            status = "Offline"
        return output, status

    # def read_url(self, stream_url):
    #     vid = cv2.VideoCapture(stream_url)
    #     return vid

    def read_fps(self, vid):
        """Function To Get FPS Of Input Video Feed"""

        fps = vid.get(cv2.CAP_PROP_FPS)
        fps = int(fps)
        print(
            f"==================================FPS IN VIDEO is {fps}==========================  "
        )
        return fps
