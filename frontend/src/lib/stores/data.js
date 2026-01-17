import {writable} from 'svelte/store';

// UsersSrore

export const userStore = writable({
    id: 'demo-user-1',
    fullName: 'Анна Подаркова',
    birthDate: '12.03.1998',
    avatarUrl: '/icons/avatar1.svg',
    showSubscriptions: true,
    ui: {
        textSize: 'medium',
        theme: 'system'
    },

});


// ЖЕЛАНИЯ
export const wishesStore = writable([
    {
        id: 1,
        title: 'Наушники с шумоподавлением',
        price: 15000,
        currency: 'RUB',
        // imageUrl: '/icons/gitf1.jpg',
        link: 'https://www.wildberries.ru/catalog/239484963/detail.aspx?size=376607842',
        description: 'McLaren Who',
        pinned: true,
        wishlistIds: [1]
        // массив id вишлистов, где лежит желание
    },
{
        id: 2,
        title: 'Наушники с шумоподавлением',
        price: 15000,
        currency: 'RUB',
        // imageUrl: '/icons/gitf1.jpg',
        link: 'https://www.wildberries.ru/catalog/239484963/detail.aspx?size=376607842',
        description: 'McLaren Who',
        pinned: true,
        wishlistIds: [1]
        // массив id вишлистов, где лежит желание
    },{
        id: 3,
        title: 'Наушники с шумоподавлением',
        price: 15000,
        currency: 'RUB',
        // imageUrl: '/icons/gitf1.jpg',
        link: 'https://www.wildberries.ru/catalog/239484963/detail.aspx?size=376607842',
        description: 'McLaren Who',
        pinned: true,
        wishlistIds: [1]
        // массив id вишлистов, где лежит желание
    },{
        id: 4,
        title: 'Наушники с шумоподавлением',
        price: 15000,
        currency: 'RUB',
        // imageUrl: '/icons/gitf1.jpg',
        link: 'https://www.wildberries.ru/catalog/239484963/detail.aspx?size=376607842',
        description: 'McLaren Who',
        pinned: true,
        wishlistIds: [1]
        // массив id вишлистов, где лежит желание
    },{
        id: 5,
        title: 'Наушники с шумоподавлением',
        price: 15000,
        currency: 'RUB',
        // imageUrl: '/icons/gitf1.jpg',
        link: 'https://www.wildberries.ru/catalog/239484963/detail.aspx?size=376607842',
        description: 'McLaren Who',
        pinned: true,
        wishlistIds: [1]
        // массив id вишлистов, где лежит желание
    },    {
        id: 6,
        title: 'Человек-Паук McLaren 720S',
        price: 999999999,
        currency: 'EUR',
        // imageUrl: '/icons/spider_man.jpg',
        description: 'Let be super cool @MARVEL',
        pinned: false,
        wishlistIds: [3]
    },
    {
        id: 101,
        title: 'Marussia В1',
        price: 38999119,
        currency: 'KZT',
        // imageUrl: '/icons/Marussia_В1.jpg',
        wishlistIds: [4]
    },
    {
        id: 102,
        title: 'Книга по фотографии',
        description: 'Повышенное артериальное давление, известное как гипертония или артериальная гипертензия представляет собой серьезное заболевание, поскольку оно может привести к таким смертельно опасным осложнениям, как инсульт и инфаркт миокарда.',
        // wishlistIds: [6]
    },

]);


// ВИШЛИСТЫ
export const wishlistsStore = writable([
    {
        id: 1,
        title: 'День рождения',
        description: 'Идеи подарков к 25-летию',
        privacy: 'restricted',      // public | restricted | private
        coverUrl: '',
        count: 31
    },

    {
        id: 3,
        title: '8-ого марта',
        description: 'Идеи подарков на 8-ого ммарта',
        privacy: 'private',
        count: 10,

    },

    {
        id: 4,
        title: '18-ого мая  ',
        description: 'Flag day',
        privacy: 'public',
        count: 13

    },

    {
        id: 6,
        title: 'Marriage',
        description: 'Shopping du siecle',
        privacy: 'public',
        count: 12


    },

]);


// Подписки (на кого я подписан)
export const subscriptionsStore = writable([
    {
        id: 'sub-5',
        subscriber_id: 'demo-user-1',
        type_sub: false,
        user: null,
        wishlist: {
            wishlist_id: 1,
            name: 'Идеи для отпуска',
            photo: '/icons/card.svg',
            user_name: 'Дмитрий Волков',
            number_of_wishes: 7
        }
    },
    {
        id: 'sub-6',
        subscriber_id: 'demo-user-1',
        type_sub: false,
        user: null,
        wishlist: {
            wishlist_id: 1,
            name: 'Гаджеты 2024',
            photo: null,
            user_name: 'Техно-блог',
            number_of_wishes: 12
        }
    },
    {
        id: 'sub-7',
        subscriber_id: 'demo-user-1',
        type_sub: false,
        user: null,
        wishlist: {
            wishlist_id: 1,
            name: 'Книжный клуб',
            photo: '/icons/book.svg',
            user_name: 'Читательское сообщество',
            number_of_wishes: 24
        }
    },
    {
        id: 'sub-8',
        subscriber_id: 'demo-user-1',
        type_sub: false,
        user: null,
        wishlist: {
            wishlist_id: 1,
            name: 'Кулинарные рецепты',
            photo: '/icons/cooking.png',
            user_name: 'Шеф-повар Антон',
            number_of_wishes: 15
        }
    }


]);


// Подписчики (кто подписан на меня)
export const subscribersStore = writable([
    {
        id: 'subscriber-1',
        user_id: 5,
        name: 'Дмитрий Смирнов',
        photo: '/icons/avatar5.svg',
        birth_date: '18.05.1990',
        is_blocked: false,
        subscription_date: '15.12.2023',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: true // Вы подписаны на этого пользователя
    },
    {
        id: 'subscriber-2',
        user_id: 6,
        name: 'Ольга Иванова',
        photo: '/icons/avatar3.svg',
        birth_date: '03.11.1994',
        is_blocked: false,
        subscription_date: '20.01.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: false // Вы НЕ подписаны на этого пользователя
    },
    {
        id: 'subscriber-3',
        user_id: 7,
        name: 'Сергей Павлов',
        photo: '/icons/avatar2.svg',
        birth_date: '29.08.1988',
        is_blocked: false,
        subscription_date: '05.02.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: true // Вы подписаны на этого пользователя
    },
    {
        id: 'subscriber-4',
        user_id: 8,
        name: 'Наталья Ковалёва',
        photo: '',
        birth_date: '14.07.1996',
        is_blocked: true, // Заблокированный пользователь
        subscription_date: '10.11.2023',
        can_view_profile: false, // Не может просматривать профиль
        can_view_wishlists: false, // Не может просматривать вишлисты
        am_i_subscribed_to_them: false
    },
    {
        id: 'subscriber-5',
        user_id: 9,
        name: 'Андрей Фёдоров',
        photo: '',
        birth_date: '22.03.1991',
        is_blocked: false,
        subscription_date: '28.02.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: false // Вы НЕ подписаны на этого пользователя
    },
    {
        id: 'subscriber-6',
        user_id: 10,
        name: 'Екатерина Николаева',
        photo: '/icons/avatar1.svg',
        birth_date: '09.09.1993',
        is_blocked: false,
        subscription_date: '12.03.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: true // Вы подписаны на этого пользователя
    },
    {
        id: 'subscriber-7',
        user_id: 11,
        name: 'Максим Орлов',
        photo: '/icons/avatar-maxim.jpg',
        birth_date: '17.12.1989',
        is_blocked: false,
        subscription_date: '01.04.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: false // Вы НЕ подписаны на этого пользователя
    },
    {
        id: 'subscriber-8',
        user_id: 12,
        name: 'Виктория Захарова',
        photo: '',
        birth_date: '06.04.1995',
        is_blocked: false,
        subscription_date: '25.03.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: true // Вы подписаны на этого пользователя
    },
    {
        id: 'subscriber-9',
        user_id: 13,
        name: 'Артём Белов',
        photo: '/icons/avatar5.svg',
        birth_date: '30.10.1992',
        is_blocked: false,
        subscription_date: '08.01.2024',
        can_view_profile: true,
        can_view_wishlists: true,
        am_i_subscribed_to_them: false // Вы НЕ подписаны на этого пользователя
    }
]);

// Настройки уведомлений 2002_4_Dass_20.12.2025
export const notificationSettingsStore = writable({
    birthdayReminders: true,
    newFollowers: true,
    postBirthdayNotifications: false,
    wishlistAccessRequests: false
});
// Анкета: интересы / что не дарить, по пользователю
export const questionnaireStore = writable({
    interests: [],
    noGifts: []
});


// --- FPS: partage profil via Telegram Mini App Direct Link ---

export const BOT_USERNAME = 'testworkwishbot';

// // IMPORTANT (FPS):
// // WEBAPP_SHORT_NAME doit être EXACTEMENT le slug du Direct Link créé dans BotFather.
// // Ex: si BotFather te montre: t.me/padari_minyebot/app  -> alors c'est "app"
// export const WEBAPP_SHORT_NAME = 'directlink';

export const APP_NAME = 'test work wish';

// URL Telegram officielle qui donne la "carte" (preview bot + bouton Lancer)
// startapp contient la valeur que tu lis via tg.initDataUnsafe.start_param
export const makeProfileTgUrl = (userId) =>
    `https://t.me/${BOT_USERNAME}/?startapp=${encodeURIComponent(
        `profile_${userId}`
    )}`;

// URL de partage Telegram (ouvre la fenêtre "choisir un chat")
// On partage TOUJOURS l’URL Telegram ci-dessus (pas ngrok, pas localhost)
export const makeProfileShareUrl = (userId, fullName = '') => {
    const url = makeProfileTgUrl(userId);
    const text = fullName ? `Профиль: ${fullName}` : `Мой профиль в «${APP_NAME}»`;
    return `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(
        text
    )}`;
};



export const otherProfilesMock = {
    "1": {
        id: 1,
        fullName: 'Иван Петров',
        birthDate: '15.07.1995',
        avatarUrl: '/icons/avatar4.svg',
        isSubscribed: true,
        publicWishlists: [
            { id: 'wl-1-1', title: 'День рождения', visibility: 'public', wishesCount: 4, iconUrl: '/icons/gift3.png' },
            { id: 'wl-1-2', title: 'Новый год', visibility: 'public', wishesCount: 2, iconUrl: '/icons/gift3.png' }
        ],
        subscriptions: [
            { id: 'sub-u-2', fullName: 'Мария Сидорова', birthDate: '22.11.1992', wishlistTitle: 'Путешествия', avatarUrl: '/icons/logo-user.svg' }
        ],
        questionnaire: {
            interests: ['Гаджеты', 'Книги', 'Путешествия'],
            noGifts: ['Алкоголь', 'Мягкие игрушки']
        }
    },

    "2": {
        id: 2,
        fullName: 'Мария Сидорова',
        birthDate: '22.11.1992',
        avatarUrl: '/icons/avatar3.svg',
        isSubscribed: false,
        publicWishlists: [
            { id: 'wl-2-1', title: '8 марта', visibility: 'public', wishesCount: 6, iconUrl: '/icons/card.svg' }
        ],
        subscriptions: [
            { id: 'sub-u-1', fullName: 'Иван Петров', birthDate: '15.07.1995', wishlistTitle: 'День рождения', avatarUrl: '/icons/logo-user.svg' }
        ],
        questionnaire: {
            interests: ['Украшения', 'Косметика', 'Сертификаты'],
            noGifts: ['Сладкое', 'Парфюм']
        }
    },

    "3": {
        id: 3,
        fullName: 'Алексей Козлов',
        birthDate: '03.09.1989',
        avatarUrl: 'avatar2.svg',
        isSubscribed: false,
        publicWishlists: [],
        subscriptions: [],
        questionnaire: { interests: ['Техника', 'Спорт'], noGifts: [] }
    },

    "4": {
        id: 4,
        fullName: 'Елена Васнецова',
        birthDate: '28.02.1997',
        avatarUrl: 'avatar1.svg',
        isSubscribed: false,
        publicWishlists: [
            { id: 'wl-4-1', title: 'Мечты', visibility: 'public', wishesCount: 1, iconUrl: '/icons/card.svg' }
        ],
        subscriptions: [],
        questionnaire: { interests: [], noGifts: ['Домашние животные'] }
    }
};
