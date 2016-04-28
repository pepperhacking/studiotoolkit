"""
Sample 8: Subscribing to events with a decorator

"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import stk.runner
import stk.services
import stk.events

class DecoratorsDemo(object):
    "Simple activity, demonstrating connecting to events with decorators."
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)

    @stk.events.on("FrontTactilTouched")
    def on_touched(self, value):
        "Callback for tablet touched."
        if value:
            self.s.ALTextToSpeech.say("Finished!")
            self.stop()

    @stk.events.on("LeftBumperPressed")
    def on_left_bumper(self, value):
        "Callback for tablet touched."
        if value:
            self.s.ALTextToSpeech.say("Bing!")

    @stk.events.on("RightBumperPressed")
    def on_right_bumper(self, value):
        "Callback for tablet touched."
        if value:
            self.s.ALTextToSpeech.say("Bong!")

    @stk.events.on("HandLeftBackTouched")
    def on_left_hand(self, value):
        "Callback for tablet touched."
        if value:
            self.s.ALTextToSpeech.say("Ping!")

    @stk.events.on("HandRightBackTouched")
    def on_right_hand(self, value):
        "Callback for tablet touched."
        if value:
            self.s.ALTextToSpeech.say("Pong!")

    def on_start(self):
        "Connects all touch events"
        self.s.ALTextToSpeech.say("Touch me!")
        # Until you call this, the decorators are not connected
        self.events.connect_decorators(self)
        print "(all connected)"

    def stop(self):
        "Standard way of stopping the application."
        self.qiapp.stop()

    def on_stop(self):
        "Cleanup"
        self.events.clear() # automatically disconnects all decorators

if __name__ == "__main__":
    stk.runner.run_activity(DecoratorsDemo)
