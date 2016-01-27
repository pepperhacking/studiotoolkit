Studio lib: **`stk/events.py`**


Basic usage
==================

Create a **`EventsHelper`** object, that will serve as a simple interface for ALMemory events and signals using a common, simple syntax.

Here is how you would block until a sensor is touched.

```python
import stk.events

events = stk.events.EventHelper(qiapp.session)

events.wait_for("FrontTactilTouched")
print "The front tactile sensor was touched!"

``` 
... and here's how one would subscribe to an event, to print something each time that sensor is touched:

```python
import stk.runner
import stk.events

class TouchDemo(object):
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)

    def on_touched(self, value):
        if value:
            print "It tickles!"

    def on_start(self):
        self.events.connect("FrontTactilTouched", self.on_touched)

stk.runner.run_activity(TouchDemo)
```

using decorators
==================

The above example can be rewritten like this:

```python
import stk.runner
import stk.events

class DecoratorsDemo(object):
    def __init__(self, qiapp):
        self.events = stk.events.EventHelper(qiapp.session)

    @stk.events.on("FrontTactilTouched")
    def on_touched(self, value):
        if value:
            print "It tickles!"

    def on_start(self):
        self.events.connect_decorators(self)

stk.runner.run_activity(DecoratorsDemo)
```

This makes it easier to keep track of your logic, especially if you have many subscriptions.

Events vs. Signals
==================

NAOqi has two related contepts:
* ALMemory events (like `FrontTactilTouched`), handled by the ALMemory module
* Signals (like `ALTabletService.onTouch`, handled by indivisual services

NAOqi uses a different syntax for both, but `stk.events` wraps the two with the same syntax, so all the examples above would work the same with keys such as `ALTabletService.onTouch`.

API details
=====

**`on(*keys)`** : a decorator for connecting the decorated method to a callback.

Methods of **`EventHelper`**:

`EventHelper` **`.__init__(session=None)`** : constructor. If you don't specify a NAOqi session, you can do so later with `.init`

`EventHelper` **`.init(session)`** : defines the NAOqi session if it wasn't done at construction.

`EventHelper` **`.connect_decorators(object)`** : Connects all decorator methods on an object.

`EventHelper` **`.connect(event, callback)`** : connect a function to an event, so that the function will be called every time the event is raised. "event" can be either an ALMemory key, or in the form signal.service. Returns a connection ID.


`EventHelper` **`.disconnect(self, event, connection_id=None)`** : if a connection ID is given, disconnect that connection to the given event. Otherwise, disconnect all connections to the given event.

`EventHelper` **`.clear()`** : Disconnects all event subscriptions..

`EventHelper` **`.get(key)`** : get a given ALMemory key.

`EventHelper` **`.set(key, value)`** : set an ALMemory key.

`EventHelper` **`.remove(key)`** : remove an ALMemory key.

`EventHelper` **`.wait_for(event)`** : Blocks until the given event is raised, and returns its value. Will raise an exception if the wait is cancelled, or if wait_for() is called again. This blocks a thread, so avoid using it too much!

`EventHelper` **`.cancel_wait()`** : Cancels the current wait, if there is one.
