Studio lib: **`robotutils.js`**

A utility library for qimessaging.js.

Includes:

* Support for remote debugging by running pages from your local computer.
* Syntactic sugar, see below

If you use this library, you don't need to link to qimessaging.js in your html, just package it in your html folder and include:

```html
<script src="js/robotutils.js"></script>
```


API reference
====

* **RobotUtils.onServices(servicesCallback, errorCallback)**, for getting services
* **RobotUtils.subscribeToALMemoryEvent(event, eventCallback, subscribeDoneCallback)**, for subscribing to ALMemory
* **RobotUtils.robotIp** - a member variable containing the address of the robot you're connecting to 

Functions you probably will not need (used internally, or for advance things):

* **RobotUtils.connect(connectedCallback, failureCallback)**, for creating a session
* **RobotUtils.session**, contains the current qimessaging.js session.

Connecting to services
====

Just use `RobotUtils.onServices` with a function whose parameters are the names of the services you want; it will be called once they are all ready:

```javascript
RobotUtils.onServices(function(ALLeds, ALTextToSpeech) {
  ALLeds.randomEyes(2.0);
  ALTextToSpeech.say("I can speak");
});
```

Optionally, you can pass a failure callback as a second parameter:

```javascript
RobotUtils.onServices(function(ALTabletService) {
  // TODO: do something cool
}, function(error) {
  alert("oh dear, I don't have a tablet ... wait, then where is this code running?");
});
```

Failure can be because you're not connecting to a robot (e.g. just opened the page in your web browser, see the "remote debugging" section below), or NAOqi is not running, or one of the services is not available, etc.


Subscribing to ALMemory
====

Use `RobotUtils.subscribeToALMemoryEvent`, passing the name of your key, and a callback to be called whenever that event is raised:

```javascript
RobotUtils.subscribeToALMemoryEvent("FrontTactilTouched", function(value) {
  alert("Head touched: " + value);
});
```

Optionally, you can pass as second parameter a callback to be called when the subscription is done.
    
`RobotUtils.subscribeToALMemoryEvent` returns a `MemoryEventSubscription` object, on which you can call .unsubscribe(), which takes as optional parameter a callback to be called when the ubsubscription is done.
    
Remote debugging
====

`robotutils.js` makes it easy to test your webpage locally, without needing to install anything to the robot: just open your page in a browser with an extra `?robot=my-robots-ip-address` after the URL.

There are three general way of using a webpage that connects to NAOqi:

* **On Pepper's tablet**, as in the vast majority of Pepper applications
* **Hosted on Pepper, but opened with a web browser** (e.g. by opening http://my-robot/apps/my-app/)
* **Hosted on your computer**

Opening the page with a web browser is useful with debugging, as you can use your browser's debug tools (element inspection, javascript console...). Directly using the page hosted on your computer is especially useful during dev, as you can edit the files and test again without needing to copy anything on the robot - this is where you need to use the query robot parameter.

In addition, if you need to dynamically fetch web content from the robot in Javascript, you can use the `RobotUtils.robotIp` variable. For example if you want to fetch an image from another app, you could do:

```javascript
var imageUrl = "/apps/another-app/images/image.gif";
if (RobotUtils.robotIp) {
  imageUrl = "http://" + RobotUtils.robotIp + imageUrl;
}
// ... do something with imageUrl;
```

That way the image will be fetched from the right location regardless of how you are accessing your page.

Older versions of NAOqi
====

robotutils.js does not work on NAOqi version 2.1 and below - typically found on NAO. robotutils.qim1.js provides the same API but with compatibility with older versions of NAOqi:

```html
<script src="js/robotutils.qim1.js"></script>
```
