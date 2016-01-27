Studio lib: **`stk/runner.py`**

This is a collection of small utilities for running a Qi Application, while making it easy to debug without installing anything on the robot.

API reference
====

For usage recommendations, see below

* **`init()`** : returns a Qi.Application object, with some debug facilities (see below)
* **`run_activity(activity_class)`** : instantiates the activity and runs it (see below)
* **`run_service(service_class)`**  : instantiates the service, registers it and runs it (see below)


A simple script
====

The most useful function is init()

```python
import stk.runner

if __name__ == "__main__":
    qiapp = stk.runner.init()

    tts = qiapp.session.service("ALTextToSpeech")
    tts.say("Hello, World!")
```

What it does on the robot
-----

Once on the robot, this is mostly equivalent to:
   
```python
import qi

qiapp = qi.Application()
...
```

... provided the script has been called with a --qi-url argument in command line (which should be the case if it's packaged properly).

When debugging locally
-----

However, installing the application on the robot takes time, and slows down iteration time.

So when using stk.runner.init(), you can also execute the application locally, in which case it will interactively ask you for your robot's IP address:

    no --qi-url parameter given; interactively getting debug robot.
    connect to which robot? (default is citadelle.local)
    

If you have qiq installed (as in this case), it will suggest that as a default, and otherwise, you can specify on which robot you want to run.


A more complete application
====

The above script is pretty simple, but you might want a more complete app, that you can start and stop. There is a helper for that, `stk.runner`**`.run_activity()`**, that expects an "activity" class. For example:


```python
import time

import stk.runner
import stk.services

class Activity(object):
    def __init__(self, qiapp):
        "Necessary: __init__ must take a qiapplication as parameter"
        self.qiapp = qiapp
        self.services = stk.services.ServiceCache(qiapp.session)

    def on_start(self):
        "Optional: Called at the start of the application."
        self.services.ALTextToSpeech.say("Let me think ...")
        time.sleep(2)
        self.services.ALTextToSpeech.say("No, nothing.")
        self.stop()

    def stop(self):
        "Optional: Standard way of stopping the activity."
        self.qiapp.stop()

    def on_stop(self):
        "Optional: Automatically called before exit (from .stop() or SIGTERM)."
        pass

if __name__ == "__main__":
    stk.runner.run_activity(Activity)
```

The class must define a **`__init__`** that takes a qiapplication as a parameter,
and may also define **`on_start`** and **`on_stop`**.
The application will then run until qiapplication.stop() is called.


A Service
====

This mostly works the same as for an activity:

```python
import qi
import stk.runner

class ALAddition(object):
    def __init__(self, qiapp):
        self.qiapp = qiapp
    
    @qi.bind(qi.Int32, [qi.Int32, qi.Int32])
    def add(self, a, b):
        "Returns the sum of two numbers"
        return a + b

    def stop(self):
        "Stops the service"
        self.qiapp.stop()

if __name__ == "__main__":
    stk.runner.run_service(ALAddition)
```

Once run (even remotely), this service is available; for example with qicli:

```bash
citadelle [0] ~ $ qicli info ALAddition --show-doc
145 [ALAddition]
  * Info:
   machine   8828e3e3-dcee-46f4-abff-5a456ada9dcb
   process   9523
   endpoints tcp://10.0.132.19:47057
             tcp://127.0.0.1:47057
  * Methods:
   100 add  Int32 (Int32,Int32)
       Returns the sum of two numbers.
   101 stop Value ()
       Stops the service.
citadelle [0] ~ $ qicli call ALAddition.add 1 2
3
```
