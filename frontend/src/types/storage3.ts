export interface FileUploadResponse {
    message: string;
    filename: string;
    file_url: string;
    content_type: string;
    size: number;
}

export interface FileDeleteResponse {
    message: string;
    file_url: string;
}

/*загрузка файла*/
export async function uploadFile(file: File, token: string): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/v1/file/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка загрузки файла');
    }
    
    return await response.json();
}

/*замена файла*/
export async function replaceFile(oldFileUrl: string, newFile: File, token: string): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file_url', oldFileUrl);
    formData.append('file', newFile);
    
    const response = await fetch('/api/v1/file/replace', {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка замены файла');
    }
    
    return await response.json();
}

/*удаление файла*/
export async function deleteFile(fileUrl: string, token: string): Promise<FileDeleteResponse> {
    const params = new URLSearchParams();
    params.append('file_url', fileUrl);
    
    const response = await fetch(`/api/v1/file/delete?${params.toString()}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка удаления файла');
    }
    
    return await response.json();
}
