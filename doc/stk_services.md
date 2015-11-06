Studio lib: **`stk/services.py`**


Basic usage
==================

Create a **`ServiceCache`** object, and it will behave as if it had all NAOqi services as members.

For example:

```python
import stk.services

services = stk.services.ServiceCache(qiapp.session)

if services.ALAddition:
    result = services.ALAddition.add(2, 2)
    services.ALTextToSpeech.say("2 and 2 are " + str(result))
else:
    services.ALTextToSpeech.say("You don't have ALAddition, so watch my eyes")
    services.ALLeds.rasta(2.0)
```

This is equivalent to:

```python
try:
    addition = session.service("ALAddition")
except RuntimeError: # service is not registered
    addition = None
    
if addition:
    addition.showWebview()
else:
    session.service("ALTextToSpeech").say("I don't have a webview")
    session.service("ALLeds").rasta(2.0)
```

So it allows you to keep your code simple and readable.


API details
=====


Methods of **`ServiceCache`**:

`ServiceCache` **`.__init__(session=None)`** : constructor. If you don't specify a session, you can do so later with `.init`

`ServiceCache` **`.init(session)`** : defines the session if it wasn't done at construction.

`ServiceCache` **`.unregister(service_name)`** : unregisters the service, if it exists.

`ServiceCache` **`.(any NAOqi module name)`** : will return the NAOqi module, or `None` if it doesn't exist.

