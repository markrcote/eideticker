function EController() {
}

EController.prototype = {
  toString: function() { return "[EController]"; },
  pageLoaded: function() {
    sendAsyncMessage('EController.PageLoaded', { });
  },
  animationFinished: function() {
    sendAsyncMessage('EController.AnimationFinished', { });
  },
  __exposedProps__: {
    'toString': 'r',
    'pageLoaded': 'r',
    'animationFinished': 'r'
  }
};

// This is a frame script, so it may be running in a content process.
// In any event, it is targeted at a specific "tab", so we listen for
// the DOMWindowCreated event to be notified about content windows
// being created in this context.

function EControllerManager() {
  addEventListener("DOMWindowCreated", this, false);
}

EControllerManager.prototype = {
  handleEvent: function handleEvent(aEvent) {
    var window = aEvent.target.defaultView;
    window.wrappedJSObject.EController = new EController(window);
  }
};

var eidetickerControllerManager = new EControllerManager();
