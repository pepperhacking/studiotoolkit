"""
Sample 7: Listening for events

Demonstrates a couple basic ways of using events.
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import stk.runner
import stk.services
import stk.events

class EventsDemo(object):
    "Simple activity, demonstrating simple ways to listen to events."
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)

    def on_touched(self, *args):
        "Callback for tablet touched."
        if args:
            self.events.disconnect("ALTabletService.onTouchDown")
            self.s.ALTextToSpeech.say("Yay!")
            self.stop()

    def on_start(self):
        "Ask to be touched, waits, and exits."
        # Two ways of waiting for events
        # 1) block until it's called
        self.s.ALTextToSpeech.say("Touch my forehead.")
        self.events.wait_for("FrontTactilTouched")
        # 1) connect a callback
        if self.s.ALTabletService:
            self.events.connect("ALTabletService.onTouchDown", self.on_touched)
            self.s.ALTextToSpeech.say("okay, now touch my tablet.")
        else:
            self.s.ALTextToSpeech.say("oh, I don't have a tablet...")
            self.stop()

    def stop(self):
        "Standard way of stopping the application."
        self.qiapp.stop()

    def on_stop(self):
        "Cleanup"
        self.events.clear()

if __name__ == "__main__":
    stk.runner.run_activity(EventsDemo)
