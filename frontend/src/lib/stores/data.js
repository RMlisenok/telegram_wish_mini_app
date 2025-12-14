import { writable } from 'svelte/store';

// UsersSrore

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




// ВИШЛИСТЫ
export const wishlistsStore = writable([
    {
        id: 1,
        title: 'День рождения',
        description: 'Идеи подарков к 25-летию',
        privacy: 'public',      // public | restricted | private
        coverUrl: '',
        count: 3
    },

    {
        id: 3,
        title: '8-ого марта ',
        description: 'Идеи подарков на 8-ого ммарта',
        privacy: 'public',
        count: 3
        // rUrl: '/icons/gift2.svg'
    },

    {
        id: 4,
        title: '18-ого мая  ',
        description: 'Flag day',
        privacy: 'public',
        count: 3

    },

    {
        id: 6,
        title: 'Marriage',
        description: 'Shopping du siecle',
        privacy: 'public',
        count: 3


    },

]);