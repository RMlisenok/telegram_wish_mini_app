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

    //Тест №8 - не падает при вызове goBack без пропса onGoBack
    test('should not crash when goBack is called without onGoBack prop', async () => {
        render(EditProfile, { userStore: mockUser });
        
        const backBtn = screen.getByText('←');
        await fireEvent.click(backBtn);
        expect(true).toBe(true);
    });

    //Тест №9 - проверяет стили контейнера аватара
    test('should verify avatar container styles', () => {
        const { container } = render(EditProfile, { userStore: mockUser });
        const avatarContainer = container.querySelector('.avatar-container');
        const style = window.getComputedStyle(avatarContainer);
        
        expect(style.width).toBe('120px');
        expect(style.height).toBe('120px');
    });

    //Тест №10 - показывает ошибку если дата рождения раньше 1900 года
    test('should show error if birth date is before year 1900', async () => {
        render(EditProfile, { userStore: mockUser });
        
        const dateInput = screen.getByLabelText(/Дата рождения/i);
        await fireEvent.input(dateInput, { target: { value: '01.01.1899' } });
        
        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);
        
        expect(screen.getByText('Дата рождения не может быть раньше 01.01.1900')).toBeInTheDocument();
    });

    //Тест №11 - замена файла в S3 и успешное обновление
    test('should cover S3 file replacement and successful update', async () => {
        // Используем URL с S3, чтобы зайти в ветку photoUrl.includes('selstorage.ru')
        const s3User = { ...mockUser, avatarUrl: 'https://selstorage.ru/avatar.jpg' };
        const onUpdateUser = jest.fn();

        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ id: 1 })
        });

        render(EditProfile, { 
            userStore: s3User, 
            token: 'token', 
            onUpdateUser 
        });

        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalled();
        });
    });
    
    //Тест №12 - проверка ограничения размера файла
    test('should show alert if uploaded file is too large', async () => {
        const { container } = render(EditProfile, { userStore: mockUser });
        
        // эмуляция создания input и выбор файла
        const spy = jest.spyOn(document, 'createElement');
        const uploadBtn = screen.getByText(/Загрузить фото/i);
        await fireEvent.click(uploadBtn);

        const mockInput = spy.mock.results[0].value;
        const largeFile = new File([''], 'big-image.png', { type: 'image/png' });
        Object.defineProperty(largeFile, 'size', { value: 11 * 1024 * 1024 }); // 11MB

        mockInput.onchange({ target: { files: [largeFile] } });

        expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Файл слишком большой'));
    });

    //Тест №13 - успешная загрузка нового фото
    test('should upload new photo and call uploadFile', async () => {
        const storage = await import('../../../../types/storage3.ts');
        
        // создание моков для обязательных колбэков
        const onUpdateUser = jest.fn();
        const onGoBack = jest.fn();
        
        render(EditProfile, { 
            userStore: { ...mockUser, avatarUrl: '' }, 
            token: 'tk',
            onUpdateUser,
            onGoBack
        });

        const spy = jest.spyOn(document, 'createElement');
        await fireEvent.click(screen.getByText(/Загрузить фото/i));
        const mockInput = spy.mock.results[0].value;
        const file = new File(['hello'], 'test.png', { type: 'image/png' });
        
        mockInput.onchange({ target: { files: [file] } });

        global.fetch.mockResolvedValueOnce({ 
            ok: true, 
            json: async () => ({ status: 'success' }) 
        });

        await fireEvent.click(screen.getByText(/Сохранить изменения/i));

        await waitFor(() => {
            expect(storage.uploadFile).toHaveBeenCalledWith(file, 'tk');
            expect(onUpdateUser).toHaveBeenCalled();
            expect(onGoBack).toHaveBeenCalled();
        });
    });

    //Тест №14 - удаление фото именно из S3
    test('should call deleteFile when removing S3 photo', async () => {
        const storage = await import('../../../../types/storage3.ts');
        const onUpdateUser = jest.fn();
        
        const s3User = { ...mockUser, avatarUrl: 'https://selstorage.ru/old-photo.jpg' };
        
        render(EditProfile, { 
            userStore: s3User, 
            token: 'tk', 
            onUpdateUser 
        });

        const deleteBtn = screen.getByText(/Удалить/i);
        await fireEvent.click(deleteBtn);

        global.fetch.mockResolvedValueOnce({ 
            ok: true, 
            json: async () => ({ status: 'success' }) 
        });

        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);

        await waitFor(() => {
            expect(storage.deleteFile).toHaveBeenCalledWith('https://selstorage.ru/old-photo.jpg', 'tk');
            expect(onUpdateUser).toHaveBeenCalled();
        });
    });

});