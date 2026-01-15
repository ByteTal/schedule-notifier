/**
 * API client for communicating with the backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiClient {
    async get(endpoint) {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    async post(endpoint, data) {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    async put(endpoint, data) {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    // API Methods
    async getClasses() {
        return await this.get('/classes');
    }

    async getSchedule(classId) {
        return await this.get(`/schedule/${classId}`);
    }

    async registerUser(deviceToken, classId, className, preferences, language) {
        return await this.post('/register', {
            device_token: deviceToken,
            class_id: classId,
            class_name: className,
            preferences,
            language
        });
    }

    async updatePreferences(deviceToken, preferences, language) {
        return await this.put('/preferences', {
            device_token: deviceToken,
            preferences,
            language
        });
    }

    async getUser(deviceToken) {
        return await this.get(`/user/${deviceToken}`);
    }

    async getChanges(classId) {
        return await this.get(`/changes/${classId}`);
    }

    async getLiveChanges(classId) {
        return await this.get(`/changes/live/${classId}`);
    }

    async testNotification(deviceToken, title, body) {
        return await this.post('/test-notification', {
            device_token: deviceToken,
            title,
            body
        });
    }
}

export const api = new ApiClient();
