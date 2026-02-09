import { writable } from 'svelte/store';

export interface TagItem {
  tag: string;
  details?: string;
}

export interface QuestionnaireData {
  interests: TagItem[];
  avoid_gifts: TagItem[];
}

export interface AvailableTag {
  id: number;
  tag_value: string;
  type_tags: boolean;
}

export const questionnaireStore = writable<QuestionnaireData>([]);

// Загружает анкету текущего пользователя
export const loadQuestionnaire = async (token: string): Promise<QuestionnaireData> => {
  const response = await fetch('/api/v1/questionnaire', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      // Если анкета не найдена, возвращаем пустую структуру
      console.warn("Анкета пользователя не найдена, возвращена пустая.");
      return { interests: [], avoid_gifts: [] };
    }
    const errorText = await response.text();
    throw new Error(`Ошибка загрузки анкеты: ${response.status} - ${errorText}`);
  }

  const data: QuestionnaireData = await response.json();
  console.log(data);

  return {
    interests: data.interests || [],
    avoid_gifts: data.avoid_gifts || []
  };
};

// Сохраняет анкету текущего пользователя
export const saveQuestionnaire = async (token: string, questionnaireData: QuestionnaireData): Promise<void> => {
  console.log(questionnaireData);

  const response = await fetch('/v1/questionnaire', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(questionnaireData),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Ошибка сохранения анкеты: ${response.status} - ${errorText}`);
  }

};

// Загружает доступные теги с бэкенда
export const loadAvailableTags = async (token: string, isInterest: boolean): Promise<string[]> => {
  const params = new URLSearchParams({ is_interest: String(isInterest) });
  const response = await fetch(`/api/v1/questionnaire/tags/available?${params}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Ошибка загрузки доступных тегов: ${response.status} - ${errorText}`);
  }

  const data = await response.json();
  console.log(data);
  return data.tags ? data.tags.map((item: {tag_value: string}) => item.tag_value) : [];
};

// Загружает анкету конкретного пользователя
export const loadUserQuestionnaire = async (token: string, userId: number): Promise<QuestionnaireData> => {
  const response = await fetch(`/api/v1/questionnaire/${userId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      console.warn(`Анкета пользователя ${userId} не найдена.`);
      return { interests: [], avoid_gifts: [] }; // Возвращает пустую, если не найдена
    }
    const errorText = await response.text();
    throw new Error(`Ошибка загрузки анкеты пользователя ${userId}: ${response.status} - ${errorText}`);
  }

  const data: QuestionnaireData = await response.json();
  return {
    interests: data.interests || [],
    avoid_gifts: data.avoid_gifts || []
  };
};
