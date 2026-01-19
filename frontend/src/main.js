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

            // Show in-app notification banner
            this.showNotificationBanner(payload);

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

    showNotificationBanner(payload) {
        // Create notification banner
        const banner = document.createElement('div');
        banner.style.cssText = `
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            max-width: 90%;
            animation: slideDown 0.3s ease;
            cursor: pointer;
        `;

        const title = payload.notification?.title || 'Notification';
        const body = payload.notification?.body || '';

        banner.innerHTML = `
            <div style="font-weight: 700; margin-bottom: 4px;">${title}</div>
            <div style="font-size: 14px; opacity: 0.9;">${body}</div>
        `;

        // Add click handler to close
        banner.addEventListener('click', () => {
            banner.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => banner.remove(), 300);
        });

        // Add to document
        document.body.appendChild(banner);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (banner.parentElement) {
                banner.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => banner.remove(), 300);
            }
        }, 5000);
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
