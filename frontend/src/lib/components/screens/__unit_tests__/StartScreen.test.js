import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';

import StartScreen from '../StartScreen.svelte';
import StartScreenEventHarness from './StartScreenEventHarness.svelte';

describe('StartScreen', () => {
  afterEach(() => {
    cleanup();
  });

  test('renders the application title, subtitle and gift image', () => {
    const { container } = render(StartScreen);

    expect(screen.getByText('Подари мне')).toBeInTheDocument();
    expect(screen.getByText('Делись желаниями и дари подарки друзьям!')).toBeInTheDocument();
    expect(screen.getByAltText('Подарок')).toHaveClass('gift-img');
    expect(container.querySelector('.start-root')).toBeTruthy();
    expect(container.querySelector('.start-content')).toBeTruthy();
  });

  test('dispatches start event when user clicks the start button', async () => {
    render(StartScreenEventHarness);

    await fireEvent.click(screen.getByText('Начать'));

    expect(screen.getByTestId('events-log')).toHaveTextContent('start');
  });
});
