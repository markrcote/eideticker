const Cu = Components.utils;
const Cc = Components.classes;
const Ci = Components.interfaces;

Cu.import("resource://gre/modules/XPCOMUtils.jsm");
Cu.import("resource://gre/modules/Services.jsm");

var jsbridge = {}; Cu.import('resource://jsbridge/modules/events.js', jsbridge);

/* XPCOM gunk */
function EControllerObserver() {}

function myDump(aMessage) {
  var consoleService = Cc["@mozilla.org/consoleservice;1"].getService(Ci.nsIConsoleService);
  consoleService.logStringMessage("EController: " + aMessage);
}

EControllerObserver.prototype = {
  classDescription: "Eideticker Controller Observer for use in testing.",
  classID: Components.ID("{67a4936d-ce4c-4090-86f5-8a52ea173c5f}"),
  contractID: "@mozilla.org/eideticker-controller-observer;1",
  QueryInterface: XPCOMUtils.generateQI([Ci.nsIObserver]),
  _xpcom_categories: [{category: "profile-after-change", service: true }],
  isFrameScriptLoaded: false,
  
  observe: function(aSubject, aTopic, aData)
  {
    if (aTopic == "profile-after-change") {
      this.init();
    } else if (!this.isFrameScriptLoaded &&
               aTopic == "chrome-document-global-created") {
      var messageManager = Cc["@mozilla.org/globalmessagemanager;1"].getService(Ci.nsIChromeFrameMessageManager);
       // Register for any messages our API needs us to handle
      messageManager.addMessageListener("EController.PageLoaded", this);
      messageManager.addMessageListener("EController.AnimationFinished", this);

      messageManager.loadFrameScript("chrome://eideticker-controller/content/contentscript.js", true);
      this.isFrameScriptLoaded = true;
    } else if (aTopic == "xpcom-shutdown") {
      this.uninit();
    }
  },

  init: function () {
    var obs = Services.obs;
    obs.addObserver(this, "xpcom-shutdown", false);
    obs.addObserver(this, "chrome-document-global-created", false);
  },

  uninit: function () {
    var obs = Services.obs;
    obs.removeObserver(this, "chrome-document-global-created", false);
  },

  receiveMessage: function(aMessage) {
    jsbridge.fireEvent(aMessage.name, {});
  }
};

const NSGetFactory = XPCOMUtils.generateNSGetFactory([EControllerObserver]);
