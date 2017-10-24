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

__version__ = "0.1.2"

__copyright__ = "Copyright 2017, Aldebaran Robotics / Softbank Robotics Europe"
__author__ = 'ekroeger'
__email__ = 'ekroeger@softbankrobotics.com'

import functools
import time
import threading

import qi

class _MultiFuture(object):
    """Internal helper for handling lists of futures.

    The callback will only be called once, with either an exception or a
    list of the right type and size.
    """
    def __init__(self, futures, callback, returntype):
        self.returntype = returntype
        self.callback = callback
        self.expecting = len(futures)
        self.values = [None] * self.expecting
        self.failed = False
        self.futures = futures
        for i, future in enumerate(futures):
            future.then(lambda fut: self.__handle_part_done(i, fut))

    def __handle_part_done(self, index, future):
        "Internal callback for when a sub-function is done."
        if self.failed:
            # We already raised an exception, don't do anything else.
            return
        assert self.expecting, "Got more callbacks than expected!"
        try:
            self.values[index] = future.value()
        except Exception as exception:
            self.failed = True
            self.callback(exception=exception)
            return
        self.expecting -= 1
        if not self.expecting:
            # We have all the values
            self.callback(self.returntype(self.values))

    def cancel(self):
        "Cancel all subfutures."
        for future in self.futures:
            future.cancel()

class FutureWrapper(object):
    "Abstract base class for objects that pretend to be a future."
    def __init__(self):
        self.running = True
        self.promise = qi.Promise(self._on_future_cancelled)
        self.future = self.promise.future()
        self._exception = ""
        self.lock = threading.Lock()

    def _on_future_cancelled(self, promise):
        """If someone from outside cancelled our future - propagate."""
        promise.setCanceled()

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
        with self.lock:
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


class GeneratorFuture(FutureWrapper):
    "Future-like object (same interface) made for wrapping a generator."
    def __init__(self, generator):
        FutureWrapper.__init__(self)
        self.generator = generator
        self.future.addCallback(self.__handle_finished)
        self.sub_future = None
        self.__ask_for_next()

    def __handle_finished(self, future):
        "Callback for when our future finished for any reason."
        if self.running:
            # promise was directly finished by someone else - cancel all!
            self.running = False
            if self.sub_future:
                self.sub_future.cancel()

    def __handle_done(self, future):
        "Internal callback for when the current sub-function is done."
        try:
            self.__ask_for_next(future.value())
        except Exception as exception:
            self.__ask_for_next(exception=exception)

    def __finish(self, value):
        "Finish and return."
        with self.lock:
            self.running = False
            self.promise.setValue(value)

    def __ask_for_next(self, arg=None, exception=None):
        "Internal - get the next function in the generator."
        if self.running:
            try:
                self.sub_future = None
                if exception:
                    future = self.generator.throw(exception)
                else:
                    future = self.generator.send(arg)
                if isinstance(future, list):
                    self.sub_future = _MultiFuture(future, self.__ask_for_next,
                                                   list)
                elif isinstance(future, tuple):
                    self.sub_future = _MultiFuture(future, self.__ask_for_next,
                                                   tuple)
                elif isinstance(future, Return):
                    # Special case: we returned a special "Return" object
                    # in this case, stop execution.
                    self.__finish(future.value)
                else:
                    future.then(self.__handle_done)
                    self.sub_future = future
            except StopIteration:
                self.__finish(None)
            except Exception as exc:
                with self.lock:
                    self._exception = exc
                    self.running = False
                    self.promise.setError(str(exc))
#                   self.__finish(None) # May not be best way of finishing?

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

def public_async_generator(func):
    """Variant of async_generator that returns an actual future.

    This allows you to expose it through a qi interface (on a service), but
    that means cancel will not stop the whole chain.
    """
    @functools.wraps(func)
    def function(*args, **kwargs):
        "Wrapped function"
        return GeneratorFuture(func(*args, **kwargs)).future
    return function

class Return(object):
    "Use to wrap a return function "
    def __init__(self, value):
        self.value = value

MICROSECONDS_PER_SECOND = 1000000

class _Sleep(FutureWrapper):
    "Helper class that behaves like an async 'sleep' function"
    def __init__(self, time_in_secs):
        FutureWrapper.__init__(self)
        time_in_microseconds = int(MICROSECONDS_PER_SECOND * time_in_secs)
        self.fut = qi.async(self.set_finished, delay=time_in_microseconds)

    def set_finished(self):
        "Inner callback, finishes the future."
        with self.lock:
            self.promise.setValue(None)

sleep = _Sleep
