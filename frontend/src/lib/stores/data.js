import {writable} from 'svelte/store';

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


// Подписки (на кого я подписан)
export const subscriptionsStore = writable([
    // structure пример, потом подменишь реальными данными
    {
        id: 'user-2',
        fullName: 'Иван Иванов',
        birthDate: '05.04.1995',
        avatarUrl: '',
        wishlistTitle: 'Новый год'
    },

    {
        id: 'u-ivan',
        fullName: 'Иван Иванов',
        birthDate: '05.04.1995',
        mainWishlistTitle: 'Новый год'
    },


    {
        id: 'sub-1',
        fullName: 'Ива нов',
        birthDate: '05.04.2005',
        mainOccasion: 'Новый год'
    },
    {
        id: 'sub-2',
        fullName: 'Катя Петрова',
        birthDate: '11.01.1998',
        mainOccasion: 'День рождения'
    },

    {
        id: 'f-1',
        fullName: 'Мари Марква',
        birthDate: '10.09.1990',
        mainOccasion: 'День рождения'
    },
    {
        id: 'f-2',
        fullName: 'Кирилл',
        birthDate: '10.10.2000',
        mainOccasion: 'Новый год'
    },

    {
        id: 'sub-4',
        fullName: 'Кат Перва',
        birthDate: '11.04.1998',
        mainOccasion: 'День рождения'
    },

    {
        id: 'u-maria',
        fullName: 'Мария Маркова',
        birthDate: '10.09.1990',
        mainWishlistTitle: 'День рождения'
    },


]);