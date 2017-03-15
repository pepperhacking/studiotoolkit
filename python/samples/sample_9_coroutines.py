"""
Sample 9: using coroutines to handle async tasks.
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import time

import stk.runner
import stk.events
import stk.services
import stk.logging
import stk.coroutines

class Activity(object):
    "Demonstrates cororoutine async control"
    APP_ID = "com.aldebaran.coroutines-demo"
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

    def on_start(self):
        "Start activity callback."
        self._run()

    @stk.coroutines.async_generator
    def _sub_run(self, thing):
        "Example sub-function"
        yield self.s.ALTextToSpeech.say("ready", _async=True)
        time.sleep(1)
        yield self.s.ALTextToSpeech.say("%s %s" % (thing, thing), _async=True)

    @stk.coroutines.async_generator
    def _run(self):
        "series of async calls turned into a future."
        try:
            reco = (yield self.s.ALMemory.getData("LastWordRecognizedErr",
                                                  _async=True))
            print "got?", reco
        except RuntimeError as exc:
            reco = "unknown"
            print "got runtime error on ALMemory", exc
        yield self.s.ALTextToSpeech.say("Last word is " + reco, _async=True)
        yield self._sub_run("dingo")
        yield self.s.ALLeds.rasta(0.5, _async=True)
        yield self.s.ALTextToSpeech.say("World", _async=True)
        self.stop()

    def stop(self):
        "Standard way of stopping the application."
        self.qiapp.stop()

    def on_stop(self):
        "Cleanup"
        self.logger.info("Application finished.")
        self.events.clear()
        print "cleanup finished"

if __name__ == "__main__":
    stk.runner.run_activity(Activity)
