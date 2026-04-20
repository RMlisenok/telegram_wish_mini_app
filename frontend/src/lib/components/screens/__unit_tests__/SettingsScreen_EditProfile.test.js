import { jest } from '@jest/globals';
import { cleanup, render, screen, fireEvent, waitFor } from '@testing-library/svelte';

// Используем unstable_mockModule для ESM
jest.unstable_mockModule('../../../../types/storage3.ts', () => ({
    uploadFile: jest.fn(() => Promise.resolve({ file_url: 'http://new-photo.jpg' })),
    replaceFile: jest.fn(() => Promise.resolve({ file_url: 'http://replaced.jpg' })),
    deleteFile: jest.fn(() => Promise.resolve({ message: 'success' }))
}));

// Динамически импортируем компонент
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

    //Тест №3 - показывает ошибку при пустом имени
    test('should show error when full name is empty', async () => {
        render(EditProfile, { userStore: { ...mockUser, fullName: '' } });
        
        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);
        
        expect(screen.getByText('Поле Имя и фамилия должно содержать от 1 до 40 символов')).toBeInTheDocument();
    });

    //Тест №4 - проверяет валидность формата даты рождения
    test('should validate birth date format', async () => {
        render(EditProfile, { userStore: mockUser });
        
        const dateInput = screen.getByLabelText(/Дата рождения/i);
        await fireEvent.input(dateInput, { target: { value: '99.99.99' } });
        
        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);
        
        expect(screen.getByText('Используйте формат ДД.ММ.ГГГГ')).toBeInTheDocument();
    });

    //Тест №5 - успешно сохраняет профиль и вызывает колбэк обновления
    test('should show error if birth date is before year 1900', async () => {
        const onUpdateUser = jest.fn();
        const onGoBack = jest.fn(); 
        
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'success' })
        });

        render(EditProfile, { 
            userStore: mockUser, 
            token: 'fake-token', 
            onUpdateUser, 
            onGoBack 
        });

        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith('/api/v1/users/me', expect.any(Object));
            expect(onUpdateUser).toHaveBeenCalled();
            expect(onGoBack).toHaveBeenCalled();
        });
    });

    //Тест №6 - удаляет фото профиля локально
    test('should remove profile photo locally', async () => {
        render(EditProfile, { userStore: mockUser });
        
        const deleteBtn = screen.getByText(/Удалить/i);
        await fireEvent.click(deleteBtn);
        
        expect(screen.getByText('ИИ')).toBeInTheDocument(); // В getInitials "Иван Иванов" превращается в "ИИ"
    });

    //Тест №7 - обрабатывает ошибку сервера при сохранении и логирует её
    test('should handle server error during save and log it', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        global.fetch.mockResolvedValueOnce({ ok: false }); // Эмуляция ошибки 500/400
        
        render(EditProfile, { userStore: mockUser });
        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);

        await waitFor(() => {
            expect(consoleSpy).toHaveBeenCalled();
            expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Не удалось сохранить изменения'));
        });
        consoleSpy.mockRestore();
    });

});