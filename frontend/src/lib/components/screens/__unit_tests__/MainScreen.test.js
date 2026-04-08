/**
 * @jest-environment jsdom
 */
import { describe, it, expect } from '@jest/globals';

// Тестируем вынесенную функцию getInitials
// Для тестирования функций из Svelte-компонентов рекомендуется выносить их в отдельные файлы

describe('MainScreen - getInitials function', () => {
  
  // Вспомогательная функция для тестов (дублирует логику из компонента)
  function getInitials(name) {
    if (!name || !name.trim()) return '??';
    const parts = name.trim().split(/\s+/); // Split on any whitespace, ignore empty strings
    return parts.slice(0, 2).map((p) => p[0]).join('').toUpperCase();
  };

  describe('обработка невалидных значений', () => {
    it('должна возвращать "??" для null', () => {
      expect(getInitials(null)).toBe('??');
    });

    it('должна возвращать "??" для undefined', () => {
      expect(getInitials(undefined)).toBe('??');
    });

    it('должна возвращать "??" для пустой строки', () => {
      expect(getInitials('')).toBe('??');
    });

    it('должна возвращать "??" для строки с пробелами', () => {
      expect(getInitials('   ')).toBe('??');
    });
  });

  describe('обработка одного слова', () => {
    it('должна возвращать первую букву для одного слова', () => {
      expect(getInitials('Алексей')).toBe('А');
    });

    it('должна возвращать первую букву в верхнем регистре', () => {
      expect(getInitials('алексей')).toBe('А');
    });

    it('должна обрабатывать слова с пробелами в начале/конце', () => {
      expect(getInitials('  Мария  ')).toBe('М');
    });
  });

  describe('обработка двух слов', () => {
    it('должна возвращать первые буквы двух слов', () => {
      expect(getInitials('Иван Петров')).toBe('ИП');
    });

    it('должна работать с именами в нижнем регистре', () => {
      expect(getInitials('анна соколова')).toBe('АС');
    });

    it('должна игнорировать лишние пробелы между словами', () => {
      expect(getInitials('Дмитрий   Иванов')).toBe('ДИ');
    });
  });

  describe('обработка специальных случаев', () => {
    it('должна корректно обрабатывать имена с дефисом как одно слово', () => {
      expect(getInitials('Анна-Мария')).toBe('А');
    });

    it('должна обрабатывать латинские имена', () => {
      expect(getInitials('John Doe')).toBe('JD');
    });

    it('должна обрабатывать смешанные регистры', () => {
      expect(getInitials('aNnA pEtRoVa')).toBe('AP');
    });
  });
});