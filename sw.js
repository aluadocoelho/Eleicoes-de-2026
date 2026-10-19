// Service worker mínimo: só serve para mostrar os avisos de novidades
// (o Chrome do Android exige isso) e abrir a página certa ao tocar no aviso.
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener("notificationclick", function (e) {
  e.notification.close();
  var tab = (e.notification.data && e.notification.data.tab) || "";
  e.waitUntil(self.clients.matchAll({type: "window", includeUncontrolled: true}).then(function (list) {
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      if (c.url.indexOf(self.registration.scope) === 0 && "focus" in c) {
        if (tab) c.postMessage({tab: tab});
        return c.focus();
      }
    }
    return self.clients.openWindow(self.registration.scope + (tab ? "#" + tab : ""));
  }));
});
