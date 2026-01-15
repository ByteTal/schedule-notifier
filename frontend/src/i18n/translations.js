/**
 * Translations for Hebrew and English
 */

export const translations = {
    he: {
        // Header
        appTitle: 'התראות מערכת שעות',
        langToggle: 'English',

        // Onboarding
        welcome: 'ברוכים הבאים',
        welcomeMessage: 'קבל התראות על שינויים במערכת השעות שלך',
        selectClass: 'בחר את הכיתה שלך',
        selectClassPlaceholder: 'בחר כיתה...',
        selectTeachers: 'בחר את המורים שלך',
        selectTeachersMessage: 'בחר את המורה שלך בכל מקצוע. תקבל התראות רק על שינויים במקצועות שבחרת.',
        noTeacher: 'לא לומד מקצוע זה',
        next: 'הבא',
        back: 'חזור',
        finish: 'סיים',
        loading: 'טוען...',

        // Home Screen
        todaySchedule: 'מערכת היום',
        recentChanges: 'שינויים אחרונים',
        viewAllChanges: 'צפה בכל השינויים',
        viewMyChanges: 'השינויים שלי',
        noRelevantChanges: 'אין שינויים רלוונטיים עבור המורים שבחרת',
        loadingChanges: 'טוען שינויים מהאתר...',
        loadingChangesNote: 'זה עשוי לקחת 20-30 שניות',
        noChanges: 'אין שינויים במערכת',
        noChangesMessage: 'כרגע אין שינויים במערכת השעות שלך',
        settings: 'הגדרות',

        // Change Types
        cancellation: 'ביטול שיעור',
        roomChange: 'שינוי חדר',
        lesson: 'שיעור',
        room: 'חדר',

        // Settings
        changeClass: 'שנה כיתה',
        updateTeachers: 'עדכן מורים',
        language: 'שפה',
        notifications: 'התראות',
        notificationsEnabled: 'התראות מופעלות',
        notificationsDisabled: 'התראות מושבתות',
        enableNotifications: 'הפעל התראות',

        // Notifications
        notificationPermission: 'אנא אפשר התראות כדי לקבל עדכונים על שינויים במערכת',
        allow: 'אפשר',

        // Errors
        error: 'שגיאה',
        errorLoadingClasses: 'שגיאה בטעינת רשימת הכיתות',
        errorLoadingSchedule: 'שגיאה בטעינת המערכת',
        errorRegistering: 'שגיאה ברישום',
        tryAgain: 'נסה שוב',

        // Progress Steps
        step1: 'כיתה',
        step2: 'מורים',
        step3: 'סיום',
    },

    en: {
        // Header
        appTitle: 'Schedule Notifications',
        langToggle: 'עברית',

        // Onboarding
        welcome: 'Welcome',
        welcomeMessage: 'Get notified about changes to your class schedule',
        selectClass: 'Select Your Class',
        selectClassPlaceholder: 'Choose a class...',
        selectTeachers: 'Select Your Teachers',
        selectTeachersMessage: 'Choose your teacher for each subject. You\'ll only receive notifications for subjects you select.',
        noTeacher: 'I don\'t learn this subject',
        next: 'Next',
        back: 'Back',
        finish: 'Finish',
        loading: 'Loading...',

        // Home Screen
        todaySchedule: 'Today\'s Schedule',
        recentChanges: 'Recent Changes',
        viewAllChanges: 'View All Changes',
        viewMyChanges: 'My Changes',
        noRelevantChanges: 'No relevant changes for your selected teachers',
        loadingChanges: 'Loading changes from website...',
        loadingChangesNote: 'This may take 20-30 seconds',
        noChanges: 'No Schedule Changes',
        noChangesMessage: 'There are currently no changes to your schedule',
        settings: 'Settings',

        // Change Types
        cancellation: 'Class Cancelled',
        roomChange: 'Room Change',
        lesson: 'Lesson',
        room: 'Room',

        // Settings
        changeClass: 'Change Class',
        updateTeachers: 'Update Teachers',
        language: 'Language',
        notifications: 'Notifications',
        notificationsEnabled: 'Notifications Enabled',
        notificationsDisabled: 'Notifications Disabled',
        enableNotifications: 'Enable Notifications',

        // Notifications
        notificationPermission: 'Please enable notifications to receive updates about schedule changes',
        allow: 'Allow',

        // Errors
        error: 'Error',
        errorLoadingClasses: 'Error loading class list',
        errorLoadingSchedule: 'Error loading schedule',
        errorRegistering: 'Error registering',
        tryAgain: 'Try Again',

        // Progress Steps
        step1: 'Class',
        step2: 'Teachers',
        step3: 'Done',
    }
};

export class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'he';
    }

    setLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('language', lang);
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'he' ? 'rtl' : 'ltr';
        document.body.dir = lang === 'he' ? 'rtl' : 'ltr';
    }

    t(key) {
        return translations[this.currentLang][key] || key;
    }

    getLanguage() {
        return this.currentLang;
    }
}

export const i18n = new I18n();
