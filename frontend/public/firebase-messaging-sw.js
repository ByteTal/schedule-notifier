/**
 * Firebase Cloud Messaging Service Worker
 * Handles background notifications
 */

importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCCkZZv14rlRsOPxzZbTdorUL5_WE6GRc0",
    authDomain: "schedule-notifier-7dd0e.firebaseapp.com",
    projectId: "schedule-notifier-7dd0e",
    storageBucket: "schedule-notifier-7dd0e.firebasestorage.app",
    messagingSenderId: "576852404893",
    appId: "1:576852404893:web:294255bfd64fe495174274"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Background message received:', payload);

    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/icon-192.png',
        badge: '/badge-72.png',
        data: payload.data
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    event.notification.close();

    // Open the app
    event.waitUntil(
        clients.openWindow('/')
    );
});
