from threading import Thread
import time

def keep_alive():
    def run():
        while True:
            time.sleep(60)
    Thread(target=run, daemon=True).start()