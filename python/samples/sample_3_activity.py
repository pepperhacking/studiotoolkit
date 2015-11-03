"""
Sample 3

A simple activity, whose structure roughly matches a Choregraphe box.

See the docstrings below for details.
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import time

import stk.runner
import stk.services

class Activity(object):
    "Demonstrates a simple activity."
    def __init__(self, qiapplication):
        "Necessary: __init__ must take a qiapplication as parameter"
        self.qiapplication = qiapplication
        self.services = stk.services.ServiceCache(qiapplication.session)

    def on_start(self):
        "Optional: Called at the start of the application."
        self.services.ALTextToSpeech.say("Let me think ...")
        time.sleep(2)
        self.services.ALTextToSpeech.say("No, nothing.")
        self.stop()

    def stop(self):
        "Optional: Standard way of stopping the activity."
        self.qiapplication.stop()

    def on_stop(self):
        "Optional: Automatically called before exit (from .stop() or SIGTERM)."
        pass

if __name__ == "__main__":
    stk.runner.run_activity(Activity)
