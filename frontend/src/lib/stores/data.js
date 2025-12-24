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
        rUrl: '/icons/2018_McLaren_720S.jpg',
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
        id: 'sub-1',
        subscriber_id: 'demo-user-1',
        type_sub: true,
        user: {
            user_id: 1,
            name: 'Иван Петров',
            photo: '',
            birth_date: '15.07.1995'
        },
        wishlist: null
    },
    {
        id: 'sub-2',
        subscriber_id: 'demo-user-1',
        type_sub: true,
        user: {
            user_id: 2,
            name: 'Мария Сидорова',
            photo: '/icons/avatar-maria.jpg',
            birth_date: '22.11.1992'
        },
        wishlist: null
    },
    {
        id: 'sub-3',
        subscriber_id: 'demo-user-1',
        type_sub: true,
        user: {
            user_id: 3,
            name: 'Алексей Козлов',
            photo: '/icons/avatar-alex.jpg',
            birth_date: '03.09.1989'
        },
        wishlist: null
    },
    {
        id: 'sub-4',
        subscriber_id: 'demo-user-1',
        type_sub: true,
        user: {
            user_id: 4,
            name: 'Елена Васнецова',
            photo: '',
            birth_date: '28.02.1997'
        },
        wishlist: null
    },
    {
        id: 'sub-5',
        subscriber_id: 'demo-user-1',
        type_sub: false,
        user: null,
        wishlist: {
            wishlist_id: 1,
            name: 'Идеи для отпуска',
            photo: '/icons/vacation.jpg',
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
            photo: '/icons/books.png',
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
            photo: '/icons/cooking.jpg',
            user_name: 'Шеф-повар Антон',
            number_of_wishes: 15
        }
    }


]);


// Подписчики (кто подписан на меня)
export const subscribersStore = writable([
    
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

export const BOT_USERNAME = 'padari_minyebot';

// IMPORTANT (FPS):
// WEBAPP_SHORT_NAME doit être EXACTEMENT le slug du Direct Link créé dans BotFather.
// Ex: si BotFather te montre: t.me/padari_minyebot/app  -> alors c'est "app"
export const WEBAPP_SHORT_NAME = 'directlink';

export const APP_NAME = 'Подари мне';

// URL Telegram officielle qui donne la "carte" (preview bot + bouton Lancer)
// startapp contient la valeur que tu lis via tg.initDataUnsafe.start_param
export const makeProfileTgUrl = (userId) =>
    `https://t.me/${BOT_USERNAME}/${WEBAPP_SHORT_NAME}?startapp=${encodeURIComponent(
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
