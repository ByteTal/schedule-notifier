/**
 * Firebase Cloud Messaging service for push notifications
 */

import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

// Firebase configuration (replace with your config)
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID
};

class NotificationService {
    constructor() {
        this.app = null;
        this.messaging = null;
        this.deviceToken = null;
    }

    async init() {
        try {
            // Initialize Firebase
            this.app = initializeApp(firebaseConfig);
            this.messaging = getMessaging(this.app);

            // Check if we already have a token
            this.deviceToken = localStorage.getItem('fcm_token');

            return true;
        } catch (error) {
            console.error('Error initializing Firebase:', error);
            return false;
        }
    }

    async requestPermission() {
        try {
            const permission = await Notification.requestPermission();

            if (permission === 'granted') {
                console.log('Notification permission granted');
                return await this.getDeviceToken();
            } else {
                console.log('Notification permission denied');
                return null;
            }
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return null;
        }
    }

    async getDeviceToken() {
        try {
            if (this.deviceToken) {
                return this.deviceToken;
            }

            const token = await getToken(this.messaging, {
                vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
            });

            if (token) {
                console.log('FCM Token:', token);
                this.deviceToken = token;
                localStorage.setItem('fcm_token', token);
                return token;
            } else {
                console.log('No registration token available');
                return null;
            }
        } catch (error) {
            console.error('Error getting device token:', error);
            return null;
        }
    }

    onMessageReceived(callback) {
        if (!this.messaging) {
            console.error('Messaging not initialized');
            return;
        }

        onMessage(this.messaging, (payload) => {
            console.log('Message received:', payload);

            // Show notification
            if (payload.notification) {
                new Notification(payload.notification.title, {
                    body: payload.notification.body,
                    icon: '/icon-192.png',
                    badge: '/badge-72.png',
                    data: payload.data
                });
            }

            // Call callback
            if (callback) {
                callback(payload);
            }
        });
    }

    isPermissionGranted() {
        return Notification.permission === 'granted';
    }

    getStoredToken() {
        return localStorage.getItem('fcm_token');
    }
}

export const notificationService = new NotificationService();
