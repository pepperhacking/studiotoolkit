"""
Helper for easily doing async tasks with coroutines.

It's mostly syntactic sugar that removes the need for .then and .andThen.

Simply:
 - make a generator function that yields futures (e.g. from qi.async)
 - add the decorator async_generator

For example:

@stk.coroutines.async_generator
def run_test(self):
    yield ALTextToSpeech.say("ready", _async=True)
    yield ALTextToSpeech.say("steady", _async=True)
    time.sleep(1)
    yield ALTextToSpeech.say("go", _async=True)

... this will turn run_test into a function that returns a future that is
valid when the call is done - and that is still cancelable (your robot will
start speaking).

As your function now returns a future, it can be used in "yield run_test()" in
another function wrapped with this decorator.
"""

__version__ = "0.1.0"

__copyright__ = "Copyright 2017, Aldebaran Robotics / Softbank Robotics Europe"
__author__ = 'ekroeger'
__email__ = 'ekroeger@softbankrobotics.com'

import functools

import qi

class GeneratorFuture(object):
    "Future-like object (same interface) made for wrapping a generator."
    def __init__(self, generator):
        self.generator = generator
        self.running = True
        self.promise = qi.Promise()
        self.future = self.promise.future()
        self._exception = ""
        self.__ask_for_next()

    def __handle_done(self, future):
        "Internal callback for when the current sub-function is done."
        try:
            self.__ask_for_next(future.value())
        except Exception as exception:
            self.__ask_for_next(exception=exception)

    def __finish(self, value):
        "Finish and return."
        self.running = False
        self.promise.setValue(value)

    def __ask_for_next(self, arg=None, exception=None):
        "Internal - get the next function in the generator."
        if self.running:
            try:
                if exception:
                    future = self.generator.throw(exception)
                else:
                    future = self.generator.send(arg)
                future.then(self.__handle_done)
            except StopIteration:
                self.__finish(None)
            except Exception as exc:
                self._exception = exc
                self.running = False
                self.promise.setError(str(exc))
#                self.__finish(None) # May not be best way of finishing?

    def then(self, callback):
        """Add function to be called when the future is done; returns a future.

        The callback will be called with a (finished) future.
        """
        if self.running: # We might want a mutex here...
            return self.future.then(callback)
        else:
            callback(self)
            # return something? (to see when we have a testcase for this...)

    def andThen(self, callback):
        """Add function to be called when the future is done; returns a future.

        The callback will be called with a return value (for now, None).
        """
        if self.running: # We might want a mutex here...
            return self.future.andThen(callback)
        else:
            callback(self.future.value()) #?
            # return something? (to see when we have a testcase for this...)

    def hasError(self):
        "Was there an error in one of the generator calls?"
        return bool(self._exception)

    def wait(self):
        "Blocks the thread until everything is finished."
        self.future.wait()

    def isRunning(self):
        "Is the sequence of generators still running?"
        return self.future.isRunning()

    def value(self):
        """Blocks the thread, and returns the final generator return value.

        For now, always returns None."""
        if self._exception:
            raise self._exception
        else:
            return self.future.value()

    def hasValue(self):
        "Tells us whether the generator 1) is finished and 2) has a value."
        # For some reason this doesn't do what I expected
        # self.future.hasValue() returns True even if we're not finished (?)
        if self.running:
            return False
        elif self._exception:
            return False
        else:
            return self.future.hasValue()

    def isFinished(self):
        "Is the generator finished?"
        return self.future.isFinished()

    def error(self):
        "Returns the error of the future."
        return self.future.error()

    def isCancelable(self):
        "Is this future cancelable? Yes, it always is."
        return True

    def cancel(self):
        "Cancel the future, and stop executing the sequence of actions."
        self.running = False
        self.promise.setCanceled()

    def isCanceled(self):
        "Has this already been cancelled?"
        return not self.running

    def addCallback(self, callback):
        "Add function to be called when the future is done."
        self.then(callback)

    # You know what? I'm not implementing unwrap() because I don't see a
    # use case.

def async_generator(func):
    """Decorator that turns a future-generator into a future.

    This allows having a function that does a bunch of async actions one
    after the other without awkward "then/andThen" syntax, returning a
    future-like object (actually a GeneratorFuture) that can be cancelled, etc.
    """
    @functools.wraps(func)
    def function(*args, **kwargs):
        "Wrapped function"
        return GeneratorFuture(func(*args, **kwargs))
    return function
