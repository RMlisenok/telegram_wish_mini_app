import { jest } from '@jest/globals';
import { cleanup, render, screen, fireEvent, waitFor } from '@testing-library/svelte';

// 1. Используем unstable_mockModule для ESM
jest.unstable_mockModule('../../../../types/storage3.ts', () => ({
    uploadFile: jest.fn(() => Promise.resolve({ file_url: 'http://new-photo.jpg' })),
    replaceFile: jest.fn(() => Promise.resolve({ file_url: 'http://replaced.jpg' })),
    deleteFile: jest.fn(() => Promise.resolve({ message: 'success' }))
}));

// 2. Динамически импортируем компонент
const { default: EditProfile } = await import('../settings/SettingsScreen_EditProfile.svelte');

const mockUser = {
    fullName: 'Иван Иванов',
    birthDate: '01.01.1990',
    avatarUrl: 'https://example.com/avatar.jpg',
    ui: { theme: 'light', textSize: 'medium' }
};

describe('EditProfile Component', () => {
    beforeEach(() => {
        global.fetch = jest.fn();
        global.alert = jest.fn();
        
        global.FileReader = class {
            readAsDataURL() {
                setTimeout(() => {
                    this.onload({ target: { result: 'data:image/png;base64,mock' } });
                }, 0);
            }
        };
    });

    afterEach(() => {
        cleanup();
        jest.clearAllMocks();
    });

    //Тест №1 - корректно отображает начальные данные пользователя
    test('should correctly display initial user data', () => {
        render(EditProfile, { userStore: mockUser });
        
        expect(screen.getByLabelText(/Имя и фамилия/i).value).toBe(mockUser.fullName);
        expect(screen.getByLabelText(/Дата рождения/i).value).toBe(mockUser.birthDate);
    });

    //Тест №2 - отображает только дату рождения в режиме birthDateOnly
    test('should display only birth date in birthDateOnly mode', () => {
        render(EditProfile, { userStore: mockUser, birthDateOnly: true });
        
        expect(screen.getByText('Укажите дату рождения')).toBeInTheDocument();
        expect(screen.queryByLabelText(/Имя и фамилия/i)).not.toBeInTheDocument();
        expect(screen.queryByText('←')).not.toBeInTheDocument();
    });

});