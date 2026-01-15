/**
 * Main application entry point
 */

import { i18n } from './i18n/translations.js';
import { notificationService } from './services/notifications.js';
import { OnboardingComponent } from './components/Onboarding.js';
import { HomeComponent } from './components/Home.js';

class App {
    constructor() {
        this.currentComponent = null;
    }

    async init() {
        // Initialize i18n
        i18n.setLanguage(i18n.getLanguage());

        // Initialize notifications
        await notificationService.init();

        // Set up notification listener
        notificationService.onMessageReceived((payload) => {
            console.log('Notification received:', payload);
            // Refresh changes if on home screen
            if (this.currentComponent instanceof HomeComponent) {
                this.render();
            }
        });

        // Render app
        this.render();

        // Set up language toggle
        this.setupLanguageToggle();
    }

    async render() {
        const loading = document.getElementById('loading');
        const content = document.getElementById('content');

        // Check if user is registered
        const isRegistered = localStorage.getItem('user_registered');

        if (!isRegistered) {
            // Show onboarding
            this.currentComponent = new OnboardingComponent(() => {
                this.render();
            });
        } else {
            // Show home screen
            this.currentComponent = new HomeComponent();
        }

        // Render component
        const componentElement = await this.currentComponent.render();

        // Clear content and add new component
        content.innerHTML = '';
        content.appendChild(this.createHeader());
        content.appendChild(componentElement);

        // Show content, hide loading
        loading.style.display = 'none';
        content.style.display = 'block';
    }

    createHeader() {
        const header = document.createElement('div');
        header.className = 'header';
        header.innerHTML = `
            <h1>${i18n.t('appTitle')}</h1>
            <button id="lang-toggle" class="lang-toggle">${i18n.t('langToggle')}</button>
        `;
        return header;
    }

    setupLanguageToggle() {
        document.addEventListener('click', (e) => {
            if (e.target.id === 'lang-toggle') {
                const newLang = i18n.getLanguage() === 'he' ? 'en' : 'he';
                i18n.setLanguage(newLang);
                this.render();
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});

// Register service worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/firebase-messaging-sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}
