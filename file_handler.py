import os
import requests
import time
import sys
from pathlib import Path
from pathvalidate import sanitize_filename
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler

BASE_PATH = 'D:/MyVods'

class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.mkv"]
    
    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        #print (event)  # print now only for degug

        if event.event_type == 'modified' and Path(event.src_path).stat().st_size > 50000000:
            # REPLAYS    
            if event.src_path[:9] == '.\Replay ':
                fname = os.path.basename(event.src_path)
                # if channel is offline we don't need to do anything, as it's an adhoc recording
                if self.check_online():
                    r = requests.get('https://decapi.me/twitch/game/moofle')
                    category = sanitize_filename(r.text)
                    path = os.path.join(BASE_PATH, category)
                    part = self.check_path(path)
                    os.rename(event.src_path, os.path.join(path, 'Replays', fname))
                else:
                    path = os.path.join(BASE_PATH, 'Adhoc')
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    if not os.path.isdir(os.path.join(path, 'Replays')):
                        os.mkdir(os.path.join(path, 'Replays'))
                    os.rename(event.src_path, os.path.join(path, 'Replays', fname))
                    
            # VODS        
            else:
                fname = os.path.basename(event.src_path)
                # if channel is offline we don't need to do anything, as it's an adhoc recording
                if self.check_online():
                    r = requests.get('https://decapi.me/twitch/game/moofle')
                    category = sanitize_filename(r.text)
                    path = os.path.join(BASE_PATH, category)
                    part = self.check_path(path)
                    fname_full = "Stream Archive - " + category + " - Part {} - ".format(part) + fname
                    print(fname_full)
                    os.rename(event.src_path, os.path.join(path, fname_full))
                else:
                    print(fname)
                    path = os.path.join(BASE_PATH, 'Adhoc')
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    os.rename(event.src_path, os.path.join(path, fname))
          
                
    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)
        
    def check_path(self, path):
        # Check if dir exists, if not return part 1. If true then return part dependant on amount of files.
        if not os.path.isdir(path):
            os.mkdir(path)
            part = 1
        if not os.path.isdir(os.path.join(path, 'Replays')):
            os.mkdir(os.path.join(path, 'Replays'))
            part = 1
        else:
            files = os.walk(path).__next__()[2]
            part = len(files) + 1
        return part
        
    def check_online(self):
        if not requests.get('https://decapi.me/twitch/uptime/moofle').text == 'moofle is offline':
            return True
        return False

if __name__ == '__main__':
    observer = Observer()
    observer.schedule(MyHandler(), path=BASE_PATH)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
