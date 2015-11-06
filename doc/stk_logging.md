Studio lib: **`stk/logging.py`**

This library provides utilities to make it easier to handle logging.

API reference
====

For usage recommendations, see below

* **`get_logger()`** : returns a Qi Logger object, with some debug facilities (see "Basic Usage" below)
* **`log_exceptions`** : A method decorator (on an object that must have a "logger" member) for logging exceptions raised (see "Exceptions" below)
* **`log_exceptions_and_return(value)`** : A method decorator that logs exceptions and returns a default value


Basic usage
====


Example

```python
"""
Sample 5: Logging

Demonstrates stk.logging (only prints to log)
"""

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
```

Running this example from Python IDE should produce something like:

```ini
no --qi-url parameter given; interactively getting debug robot.
connect to which robot? (default is citadelle.local) 
[I] 5736 com.aldebaran.example5: I'm writing to the log.
[I] 5736 com.aldebaran.example5: Okay I'll stop now.
[W] 5736 com.aldebaran.example5: I've been stopped with .stop().
[E] 5731 com.aldebaran.example5: My process is dyyyyyiiiiinnggggg ...
```
Running it on the robot (in NAOqi 2.4) should produce those logs in /var/log/naoqi/servicemanager/(your service's name).

You will also be able to see these logs in choregraphe or monitor (where you can filter them).


Handling Exceptions
====================

A common annoyance with working with NAOqi is that if an exeption happens in your method, exceptions raised may be silently ignored. this happens in these cases:

* With qi.async(my_function) (though you can check on the future returned by that call whether it has an error)
* With calls to service methods ALMyService.myMethod() (however the exception will be raised on the caller's side)
* With callbacks to ALMemory events and signals

This is sometimes what you want, but it often means you'll be in a situation where your code is failing for stupid reasons, but none of that appears in your logs.

Here's a service that logs it's exceptions:

```python
"""
Sample 6: Exceptions

Demonstrates decorators for exception handling
"""

import stk.runner
import stk.logging

class ALLoggerDemo(object):
    "Simple activity, demonstrating logging and exceptions"
    APP_ID = "com.aldebaran.example6"
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

    @stk.logging.log_exceptions
    def compute_arithmetic_quotient(self, num_a, num_b):
        "Do a complicated operation on the given numbers."
        return num_a / num_b

    @stk.logging.log_exceptions_and_return(False)
    def is_lucky(self, number):
        "Is this number lucky?"
        return (1.0 / number) < 0.5

    def stop(self):
        "Standard way of stopping the activity."
        self.qiapp.stop()

if __name__ == "__main__":
    stk.runner.run_service(ALLoggerDemo)
```

So there are two decorators:

**@stk.logging.log_exceptions** Just prints the exception to the log (in this case, divide by zero):

 
```ini
[E] 6607 com.aldebaran.example6: Traceback (most recent call last):
  File "/home/ekroeger/dev/studiotoolkit/python/stk/logging.py", line 37, in wrapped
    return func(self, *args)
  File "/home/ekroeger/dev/studiotoolkit/python/samples/sample_6_exceptions.py", line 20, in compute_arithmetic_quotient
    return num_a / num_b
ZeroDivisionError: long division or modulo by zero
```

The caller still gets the exceptions (as if it was not decorated):

```ini
citadelle [0] ~ $ qicli call ALLoggerDemo.compute_arithmetic_quotient 1 0
ERROR: ZeroDivisionError: long division or modulo by zero
```

**@stk.logging.log_exceptions_and_return** allows you to specify a default value to return when an exception is raised, so that the caller never sees the exceptions:

```ini
citadelle [err 1] ~ $ qicli call ALLoggerDemo.is_lucky 3
true
citadelle [0] ~ $ qicli call ALLoggerDemo.is_lucky 0
false
```

These must be attached by an object with a "logging" member (from the helper above).

**/!\ ** Be careful not to overuse `@log_exceptions_and_return`; it can be a convenient, but it amounts to catching *all* exceptions and hiding them (from the caller), which is discouraged in Python (and other languages) because it makes it harder to find mistakes in your code - see the discussion of Exceptions in [The Programming Recommendations of PEP 8](https://www.python.org/dev/peps/pep-0008/#programming-recommendations).

It is usually better to either:

* handle exceptions yourself in your methods (if they are "expected" e.g. you're running on the wrong robot, your robot doesn't have the internet...) in which case you don't need to print a full stack trace in the log, or
* raise the exception on the caller side (as happens with no decorator, or with `@log_exceptions`), so that if he is the cause of the problem (e.g. passing you malformed data), he can be aware of it, and solve the problem or handle that case.

There's the usual tradeoff between development - where you want your code to crash as soon as something goes even slightly wrong, and give you as much information as possible - and production - where you want a robust system that gracefully hides errors from the person interacting with the robot.