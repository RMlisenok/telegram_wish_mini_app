export interface User {
    id: string;
    fullName: string;
    birthDate: Date;
    avatarUrl: string;
    showSubscriptions: boolean;
    ui: {
        textSize: 'small' | 'medium' | 'large';
        theme: 'light' | 'dark' | 'system';
    };
}