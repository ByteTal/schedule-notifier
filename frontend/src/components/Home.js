/**
 * Home screen component showing schedule and changes
 */

import { api } from '../services/api.js';
import { i18n } from '../i18n/translations.js';

export class HomeComponent {
    constructor() {
        this.classId = localStorage.getItem('class_id');
        this.className = localStorage.getItem('class_name');
        this.changes = [];
        this.allChanges = [];
        this.showingAllChanges = false;
        this.selectedTeachers = this.getSelectedTeachers();
    }

    getSelectedTeachers() {
        // Get teacher preferences from localStorage
        const deviceToken = localStorage.getItem('fcm_token');
        if (!deviceToken) return [];

        // For now, we'll fetch this from the API when rendering
        return [];
    }

    async render() {
        const container = document.createElement('div');
        container.className = 'container fade-in';

        container.innerHTML = `
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h2 class="card-title" style="margin: 0;">${this.className}</h2>
                    <button id="settings-btn" class="btn btn-secondary" style="padding: 8px 16px;">
                        ⚙️ ${i18n.t('settings')}
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3 class="card-title" style="margin: 0;">${i18n.t('recentChanges')}</h3>
                    <button id="toggle-all-btn" class="btn btn-secondary" style="padding: 8px 16px; font-size: 14px;">
                        👁️ ${i18n.t('viewAllChanges') || 'View All'}
                    </button>
                </div>
                <div id="changes-list">
                    <div style="text-align: center; padding: 40px 20px;">
                        <div class="spinner" style="margin: 0 auto 16px;"></div>
                        <p>${i18n.t('loadingChanges') || 'טוען שינויים מהאתר...'}</p>
                        <p style="font-size: 14px; opacity: 0.7;">${i18n.t('loadingChangesNote') || 'זה עשוי לקחת 20-30 שניות'}</p>
                    </div>
                </div>
            </div>
        `;

        // Load changes
        await this.loadChanges(container);

        // Settings button
        container.querySelector('#settings-btn').addEventListener('click', () => {
            this.showSettings();
        });

        // Toggle all changes button
        container.querySelector('#toggle-all-btn').addEventListener('click', () => {
            this.showingAllChanges = !this.showingAllChanges;
            const btn = container.querySelector('#toggle-all-btn');
            btn.textContent = this.showingAllChanges ?
                `👁️ ${i18n.t('viewMyChanges') || 'My Changes'}` :
                `👁️ ${i18n.t('viewAllChanges') || 'View All'}`;
            this.renderChanges(container);
        });

        return container;
    }

    async loadChanges(container) {
        try {
            // Get user preferences first
            const deviceToken = localStorage.getItem('fcm_token');
            if (deviceToken) {
                try {
                    const userResponse = await api.getUser(deviceToken);
                    this.selectedTeachers = Object.values(userResponse.user.preferences || {});
                } catch (e) {
                    console.log('Could not load user preferences:', e);
                }
            }

            // Use live changes endpoint to get real-time data from website
            const response = await api.getLiveChanges(this.classId);
            this.allChanges = response.changes;

            this.renderChanges(container);

        } catch (error) {
            container.querySelector('#changes-list').innerHTML = `
                <p style="color: var(--danger);">${i18n.t('error')}: ${error.message}</p>
            `;
        }
    }

    renderChanges(container) {
        const changesList = container.querySelector('#changes-list');

        // Filter changes based on toggle
        const changesToShow = this.showingAllChanges ?
            this.allChanges :
            this.allChanges.filter(change => this.selectedTeachers.includes(change.teacher));

        if (changesToShow.length === 0) {
            const message = this.showingAllChanges ?
                i18n.t('noChangesMessage') :
                (i18n.t('noRelevantChanges') || 'אין שינויים רלוונטיים עבור המורים שבחרת');

            changesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📅</div>
                    <h3>${i18n.t('noChanges')}</h3>
                    <p>${message}</p>
                </div>
            `;
        } else {
            changesList.innerHTML = changesToShow.map(change => `
                <div class="change-item ${change.change_type}">
                    <div class="change-header">
                        <span class="change-type ${change.change_type}">
                            ${i18n.t(change.change_type)}
                        </span>
                        <span class="change-date">${change.date}</span>
                    </div>
                    <div class="change-details">
                        <span class="change-teacher">${change.teacher}</span> - 
                        ${i18n.t('lesson')} ${change.lesson_number}
                        ${change.new_room ? `<br>${i18n.t('room')}: ${change.new_room}` : ''}
                    </div>
                </div>
            `).join('');
        }
    }

    showSettings() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;

        modal.innerHTML = `
            <div class="card" style="max-width: 400px; width: 90%; margin: 20px;">
                <h3 class="card-title">${i18n.t('settings')}</h3>
                <div style="margin-bottom: 16px;">
                    <button class="btn btn-secondary btn-full" onclick="localStorage.clear(); location.reload();">
                        ${i18n.t('changeClass')}
                    </button>
                </div>
                <div style="margin-bottom: 16px;">
                    <button class="btn btn-secondary btn-full" id="close-modal">
                        ${i18n.t('back')}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.id === 'close-modal') {
                modal.remove();
            }
        });
    }
}
