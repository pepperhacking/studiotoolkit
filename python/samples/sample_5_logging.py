"""
Sample 5: Logging

Demonstrates stk.logging (only prints to log)
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import time

import stk.runner
import stk.logging

class ActivityWithLogging(object):
    "Simple activity, demonstrating logging"
    APP_ID = "com.aldebaran.example5"
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

    def on_start(self):
        "Called at the start of the application."
        self.logger.info("I'm writing to the log.")
        time.sleep(4) # you can try stopping the process while it sleeps.
        self.logger.info("Okay I'll stop now.")
        self.stop()

    def stop(self):
        "Standard way of stopping the activity."
        self.logger.warning("I've been stopped with .stop().")
        self.qiapp.stop()

    def on_stop(self):
        "Called after the app is stopped."
        self.logger.error("My process is dyyyyyiiiiinnggggg ...")

if __name__ == "__main__":
    stk.runner.run_activity(ActivityWithLogging)
