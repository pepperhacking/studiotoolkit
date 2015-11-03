"""
Sample 1: just using robot_app.init() to get a QiApplication object.

You should be able to run this on your computer and have it connect to
the robot remotely - you should be prompted to enter your robot's address.

As an extra, if you use qiq, it will suggest using that by default.

You can also add --qi-url <YOUR-ROBOT> as a command-line parameter (this should
be the way it's configured when installed on the robot).
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import stk.runner

if __name__ == "__main__":
    qiapp = stk.runner.init()

    tts = qiapp.session.service("ALTextToSpeech")
    tts.say("Hello, World!")
