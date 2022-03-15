
#!/usr/bin/env python

# NOTE: Line numbers of this example are referenced in the user guide.
# Don't forget to update the user guide after every modification of this example.

import csv
import math
import os
import queue
import shlex
import subprocess
import tempfile
import threading
import time

import tkinter
from tkinter import *
from  tkinter import ttk
import random
import csv
from tkintermapview import TkinterMapView

import olympe

from olympe.messages.ardrone3.Piloting import TakeOff, Landing
from olympe.messages.ardrone3.Piloting import moveBy
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
from olympe.messages.ardrone3.PilotingSettings import MaxTilt
from olympe.messages.ardrone3.GPSSettingsState import GPSFixStateChanged
from olympe.messages.skyctrl.CoPiloting import setPilotingSource


from olympe.messages.ardrone3.PilotingState import (
    PositionChanged,
    AlertStateChanged,
    FlyingStateChanged,
    NavigateHomeStateChanged,
    SpeedChanged
)


from olympe.video.renderer import PdrawRenderer


olympe.log.update_config({"loggers": {"olympe": {"level": "WARNING"}}})

DRONE_IP = "192.168.53.1"
DRONE_RTSP_PORT = os.environ.get("DRONE_RTSP_PORT")


root_tk = tkinter.Tk()
root_tk.geometry(f"{600}x{400}")
root_tk.title("map_view_simple_example.py")

# create map widget
map_widget = TkinterMapView(root_tk, width=600, height=400, corner_radius=0)
map_widget.pack(fill="both", expand=True, side=LEFT)

map_widget.set_address("Durham North Carolina", marker=True)

id = 1
rows = []
prev = None

def save_csv():
    print("csv")
    f = open('test.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['id', 'lat', 'long'])
    writer.writerows(rows)
    f.close()

def run_drone(lat, long):
    global prev, id, rows
    lat = random.uniform(35.9, 36.1)
    long = random.uniform(-78.9, -79.1)
    rows.append([id, lat, long])
    marker = map_widget.set_marker(lat, long, text=str("marker") + str(id))

    if (prev is not None):
        path_1 = map_widget.set_path([marker.position, prev.position])
    table.insert(parent='',index='end',iid=id,text='',
        values=(str(id),str(lat),str(long)))
    prev = marker
    id += 1



class FlightListener(olympe.EventListener):

    @olympe.listen_event(FlyingStateChanged() | AlertStateChanged() |
        NavigateHomeStateChanged())
    def onStateChanged(self, event, scheduler):
        print("{} = {}".format(event.message.name, event.args["state"]))
        print(time.time())

    @olympe.listen_event(PositionChanged(_policy="wait"))
    def onPositionChanged(self, event, scheduler):
        print(
            "latitude = {latitude} longitude = {longitude} altitude = {altitude}".format(
                **event.args
            )
        )
        run_drone(event.args["latitude"], event.args["longitude"])
        print(time.time())

    @olympe.listen_event(SpeedChanged(_policy="wait"))
    def onSpeedChanged(self, event, scheduler):
        print("speedXYZ = ({speedX}, {speedY}, {speedZ})".format(**event.args))




class StreamingExample:
    def __init__(self):
        # Create the olympe.Drone object from its IP address
        self.drone = olympe.Drone(DRONE_IP)
        

    # drone.disconnect()
        self.tempd = tempfile.mkdtemp(prefix="olympe_streaming_test_")
        print("Olympe streaming example output dir: {}".format(self.tempd))
        self.h264_frame_stats = []
        self.h264_stats_file = open(os.path.join(self.tempd, "h264_stats.csv"), "w+")
        self.h264_stats_writer = csv.DictWriter(
            self.h264_stats_file, ["fps", "bitrate"]
        )
        self.h264_stats_writer.writeheader()
        self.frame_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self.yuv_frame_processing)
        self.renderer = None

    def start(self):
        # Connect the the drone
        assert self.drone.connect(retry=3)
        self.drone(setPilotingSource(source=0))
        if DRONE_RTSP_PORT is not None:
            self.drone.streaming.server_addr = f"{DRONE_IP}:{DRONE_RTSP_PORT}"

        # You can record the video stream from the drone if you plan to do some
        # post processing.
        # self.drone.streaming.set_output_files(
        #     video=os.path.join(self.tempd, "streaming.mp4"),
        #     metadata=os.path.join(self.tempd, "streaming_metadata.json"),
        # )

        # Setup your callback functions to do some live video processing
        self.drone.streaming.set_callbacks(
            raw_cb=self.yuv_frame_cb,
            h264_cb=self.h264_frame_cb,
            start_cb=self.start_cb,
            end_cb=self.end_cb,
            flush_raw_cb=self.flush_cb,
        )
        # Start video streaming
        self.drone.streaming.start()
        self.renderer = PdrawRenderer(pdraw=self.drone.streaming)
        self.running = True
        self.processing_thread.start()

    def stop(self):
        self.running = False
        self.processing_thread.join()
        if self.renderer is not None:
            self.renderer.stop()
        # Properly stop the video stream and disconnect
        assert self.drone.streaming.stop()
        assert self.drone.disconnect()
        self.h264_stats_file.close()

    def yuv_frame_cb(self, yuv_frame):
        """
        This function will be called by Olympe for each decoded YUV frame.
            :type yuv_frame: olympe.VideoFrame
        """
        yuv_frame.ref()
        self.frame_queue.put_nowait(yuv_frame)

    def yuv_frame_processing(self):
        while self.running:
            try:
                yuv_frame = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            # You should process your frames here and release (unref) them when you're done.
            # Don't hold a reference on your frames for too long to avoid memory leaks and/or memory
            # pool exhaustion.
            yuv_frame.unref()

    def flush_cb(self, stream):
        if stream["vdef_format"] != olympe.VDEF_I420:
            return True
        while not self.frame_queue.empty():
            self.frame_queue.get_nowait().unref()
        return True

    def start_cb(self):
        pass

    def end_cb(self):
        pass

    def h264_frame_cb(self, h264_frame):
        """
        This function will be called by Olympe for each new h264 frame.
            :type yuv_frame: olympe.VideoFrame
        """

        # Get a ctypes pointer and size for this h264 frame
        frame_pointer, frame_size = h264_frame.as_ctypes_pointer()

        # For this example we will just compute some basic video stream stats
        # (bitrate and FPS) but we could choose to resend it over an another
        # interface or to decode it with our preferred hardware decoder..

        # Compute some stats and dump them in a csv file
        info = h264_frame.info()
        frame_ts = info["ntp_raw_timestamp"]
        if not bool(info["is_sync"]):
            while len(self.h264_frame_stats) > 0:
                start_ts, _ = self.h264_frame_stats[0]
                if (start_ts + 1e6) < frame_ts:
                    self.h264_frame_stats.pop(0)
                else:
                    break
            self.h264_frame_stats.append((frame_ts, frame_size))
            h264_fps = len(self.h264_frame_stats)
            h264_bitrate = 8 * sum(map(lambda t: t[1], self.h264_frame_stats))
            self.h264_stats_writer.writerow({"fps": h264_fps, "bitrate": h264_bitrate})

    def show_yuv_frame(self, window_name, yuv_frame):
        # the VideoFrame.info() dictionary contains some useful information
        # such as the video resolution
        info = yuv_frame.info()

        height, width = (  # noqa
            info["raw"]["frame"]["info"]["height"],
            info["raw"]["frame"]["info"]["width"],
        )

        # yuv_frame.vmeta() returns a dictionary that contains additional
        # metadata from the drone (GPS coordinates, battery percentage, ...)

        # convert pdraw YUV flag to OpenCV YUV flag
        # import cv2
        # cv2_cvt_color_flag = {
        #     olympe.VDEF_I420: cv2.COLOR_YUV2BGR_I420,
        #     olympe.VDEF_NV12: cv2.COLOR_YUV2BGR_NV12,
        # }[yuv_frame.format()]

    def fly(self):
        # Takeoff, fly, land, ...
        # print("Takeoff if necessary...")
        # self.drone(
        #     FlyingStateChanged(state="hovering", _policy="check")
        #     | FlyingStateChanged(state="flying", _policy="check")
        #     | (
        #         GPSFixStateChanged(fixed=1, _timeout=10, _policy="check_wait")
        #         >> (
        #             TakeOff(_no_expect=True)
        #             & FlyingStateChanged(
        #                 state="hovering", _timeout=10, _policy="check_wait"
        #             )
        #         )
        #     )
        # ).wait()
        # self.drone(MaxTilt(40)).wait().success()
        # for i in range(4):
        #     print("Moving by ({}/4)...".format(i + 1))
        #     self.drone(moveBy(10, 0, 0, math.pi, _timeout=20)).wait().success()

        # print("Landing...")
        # self.drone(Landing() >> FlyingStateChanged(state="landed", _timeout=5)).wait()
        # print("Landed\n")
        with FlightListener(self.drone):
            while True:
                x=1


    def replay_with_vlc(self):
        # Replay this MP4 video file using VLC
        mp4_filepath = os.path.join(self.tempd, "streaming.mp4")
        subprocess.run(shlex.split(f"vlc --play-and-exit {mp4_filepath}"), check=True)


def test_streaming():
    streaming_example = StreamingExample()
    # Start the video stream
    streaming_example.start()
    # Perform some live video processing while the drone is flying
    streaming_example.fly()
    # Stop the video stream
    streaming_example.stop()
    # Recorded video stream postprocessing
    # streaming_example.replay_with_vlc()


if __name__ == "__main__":

    frame = Frame(root_tk)
    frame.pack(side=RIGHT, expand=True)    

    #create button to run drone code
    button = Button(frame, text ='Run Drone Code', command=run_drone)  
    button.pack(side=BOTTOM)

    #create button to save csv
    button = Button(frame, text ='Save as CSV', command=save_csv)  
    button.pack(side=BOTTOM)

    table = ttk.Treeview(frame)

    table['columns'] = ('id', 'lat', 'long')

    table.column("#0", width=0,  stretch=NO)
    table.column("id",anchor=CENTER, width=80)
    table.column("lat",anchor=CENTER,width=80)
    table.column("long",anchor=CENTER,width=80)

    table.heading("#0",text="",anchor=CENTER)
    table.heading("id",text="Id",anchor=CENTER)
    table.heading("lat",text="Lat",anchor=CENTER)
    table.heading("long",text="Long",anchor=CENTER)

    table.pack(side=TOP,expand=True)
    root_tk.mainloop()
    print("here")
    test_streaming()