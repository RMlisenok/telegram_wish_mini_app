import { writable } from 'svelte/store';

export const userStore = writable({
    id: 'demo-user-1',
    fullName: 'Анна Подаркова',
    birthDate: '12.03.1998',
    avatarUrl: '',
    showSubscriptions: true,
    ui: {
        textSize: 'medium',
        theme: 'system'
    },

});




