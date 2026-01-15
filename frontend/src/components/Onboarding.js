/**
 * Onboarding component for class and teacher selection
 */

import { api } from '../services/api.js';
import { i18n } from '../i18n/translations.js';
import { notificationService } from '../services/notifications.js';

export class OnboardingComponent {
    constructor(onComplete) {
        this.onComplete = onComplete;
        this.currentStep = 1;
        this.selectedClass = null;
        this.selectedClassName = '';
        this.subjects = [];
        this.selectedTeachers = {};
    }

    async render() {
        const container = document.createElement('div');
        container.className = 'container fade-in';

        // Progress steps
        container.innerHTML = `
            <div class="progress-steps">
                <div class="progress-step ${this.currentStep >= 1 ? 'active' : ''} ${this.currentStep > 1 ? 'completed' : ''}">
                    <div class="progress-step-circle">1</div>
                    <div class="progress-step-label">${i18n.t('step1')}</div>
                </div>
                <div class="progress-step ${this.currentStep >= 2 ? 'active' : ''} ${this.currentStep > 2 ? 'completed' : ''}">
                    <div class="progress-step-circle">2</div>
                    <div class="progress-step-label">${i18n.t('step2')}</div>
                </div>
                <div class="progress-step ${this.currentStep >= 3 ? 'active' : ''}">
                    <div class="progress-step-circle">3</div>
                    <div class="progress-step-label">${i18n.t('step3')}</div>
                </div>
            </div>
            
            <div id="step-content"></div>
        `;

        this.renderStep(container.querySelector('#step-content'));

        return container;
    }

    async renderStep(container) {
        if (this.currentStep === 1) {
            await this.renderClassSelection(container);
        } else if (this.currentStep === 2) {
            await this.renderTeacherSelection(container);
        } else if (this.currentStep === 3) {
            await this.renderCompletion(container);
        }
    }

    async renderClassSelection(container) {
        container.innerHTML = `
            <div class="card">
                <h2 class="card-title">${i18n.t('selectClass')}</h2>
                <div class="form-group">
                    <label class="form-label">${i18n.t('selectClass')}</label>
                    <select id="class-select" class="form-select">
                        <option value="">${i18n.t('selectClassPlaceholder')}</option>
                    </select>
                </div>
                <button id="next-btn" class="btn btn-primary btn-full" disabled>
                    ${i18n.t('next')}
                </button>
            </div>
        `;

        // Load classes
        try {
            const response = await api.getClasses();
            const select = container.querySelector('#class-select');

            response.classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls.id;
                option.textContent = cls.name;
                select.appendChild(option);
            });

            // Event listeners
            select.addEventListener('change', (e) => {
                this.selectedClass = e.target.value;
                this.selectedClassName = e.target.options[e.target.selectedIndex].text;
                container.querySelector('#next-btn').disabled = !this.selectedClass;
            });

            container.querySelector('#next-btn').addEventListener('click', () => {
                this.currentStep = 2;
                this.renderStep(container.parentElement.querySelector('#step-content'));
            });

        } catch (error) {
            container.innerHTML = `
                <div class="card">
                    <p style="color: var(--danger);">${i18n.t('errorLoadingClasses')}: ${error.message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        ${i18n.t('tryAgain')}
                    </button>
                </div>
            `;
        }
    }

    async renderTeacherSelection(container) {
        container.innerHTML = `
            <div class="card">
                <h2 class="card-title">${i18n.t('selectTeachers')}</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    ${i18n.t('selectTeachersMessage')}
                </p>
                <div id="teacher-list">${i18n.t('loading')}</div>
                <div style="display: flex; gap: 12px; margin-top: 24px;">
                    <button id="back-btn" class="btn btn-secondary" style="flex: 1;">
                        ${i18n.t('back')}
                    </button>
                    <button id="finish-btn" class="btn btn-primary" style="flex: 2;">
                        ${i18n.t('finish')}
                    </button>
                </div>
            </div>
        `;

        // Load schedule
        try {
            const response = await api.getSchedule(this.selectedClass);
            this.subjects = response.subjects;

            const teacherList = container.querySelector('#teacher-list');
            teacherList.innerHTML = '';

            this.subjects.forEach(subject => {
                const item = document.createElement('div');
                item.className = 'teacher-item';
                item.innerHTML = `
                    <div class="teacher-subject">${subject.subject}</div>
                    <div class="teacher-options" data-subject="${subject.subject}">
                        ${subject.teachers.map(teacher => `
                            <div class="teacher-option" data-teacher="${teacher}">
                                ${teacher}
                            </div>
                        `).join('')}
                        <div class="teacher-option none" data-teacher="">
                            ${i18n.t('noTeacher')}
                        </div>
                    </div>
                `;
                teacherList.appendChild(item);
            });

            // Event listeners for teacher selection
            teacherList.querySelectorAll('.teacher-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    const subject = e.target.closest('.teacher-options').dataset.subject;
                    const teacher = e.target.dataset.teacher;

                    // Deselect others in same subject
                    e.target.closest('.teacher-options').querySelectorAll('.teacher-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });

                    // Select this one
                    e.target.classList.add('selected');

                    // Store selection
                    if (teacher) {
                        this.selectedTeachers[subject] = teacher;
                    } else {
                        delete this.selectedTeachers[subject];
                    }
                });
            });

            // Back button
            container.querySelector('#back-btn').addEventListener('click', () => {
                this.currentStep = 1;
                this.renderStep(container.parentElement.querySelector('#step-content'));
            });

            // Finish button
            container.querySelector('#finish-btn').addEventListener('click', async () => {
                await this.completeOnboarding();
            });

        } catch (error) {
            container.querySelector('#teacher-list').innerHTML = `
                <p style="color: var(--danger);">${i18n.t('errorLoadingSchedule')}: ${error.message}</p>
            `;
        }
    }

    async renderCompletion(container) {
        container.innerHTML = `
            <div class="card" style="text-align: center;">
                <div style="font-size: 64px; margin-bottom: 16px;">✅</div>
                <h2 class="card-title">${i18n.t('welcome')}</h2>
                <p style="color: var(--text-secondary);">
                    ${i18n.t('welcomeMessage')}
                </p>
            </div>
        `;
    }

    async completeOnboarding() {
        try {
            // Request notification permission
            let deviceToken = notificationService.getStoredToken();

            if (!deviceToken) {
                deviceToken = await notificationService.requestPermission();
            }

            if (!deviceToken) {
                alert('Please enable notifications to receive updates');
                return;
            }

            // Register user
            const response = await api.registerUser(
                deviceToken,
                this.selectedClass,
                this.selectedClassName,
                this.selectedTeachers,
                i18n.getLanguage()
            );

            if (response.success) {
                // Save to localStorage
                localStorage.setItem('user_registered', 'true');
                localStorage.setItem('class_id', this.selectedClass);
                localStorage.setItem('class_name', this.selectedClassName);

                this.currentStep = 3;
                const container = document.querySelector('#step-content');
                await this.renderCompletion(container);

                // Redirect to home after 2 seconds
                setTimeout(() => {
                    this.onComplete();
                }, 2000);
            }

        } catch (error) {
            alert(`${i18n.t('errorRegistering')}: ${error.message}`);
        }
    }
}
