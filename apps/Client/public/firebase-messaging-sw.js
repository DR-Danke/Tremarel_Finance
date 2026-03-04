/**
 * Firebase Messaging Service Worker for push notification reception.
 *
 * This is a minimal service worker that handles incoming push events
 * and displays browser notifications. Full Firebase SDK integration
 * (firebase-app + firebase-messaging npm packages) is required for
 * token management, permission dialogs, and topic subscriptions.
 */

/* eslint-disable no-restricted-globals */

self.addEventListener('push', function (event) {
  const defaultTitle = 'Restaurant OS'
  const defaultBody = 'Nueva notificacion'

  let title = defaultTitle
  let body = defaultBody
  let data = {}

  if (event.data) {
    try {
      const payload = event.data.json()
      title = (payload.notification && payload.notification.title) || defaultTitle
      body = (payload.notification && payload.notification.body) || defaultBody
      data = payload.data || {}
    } catch (e) {
      body = event.data.text() || defaultBody
    }
  }

  const options = {
    body: body,
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    data: data,
  }

  event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', function (event) {
  event.notification.close()

  event.waitUntil(
    self.clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then(function (clientList) {
        for (var i = 0; i < clientList.length; i++) {
          var client = clientList[i]
          if ('focus' in client) {
            return client.focus()
          }
        }
        if (self.clients.openWindow) {
          return self.clients.openWindow('/')
        }
      })
  )
})
