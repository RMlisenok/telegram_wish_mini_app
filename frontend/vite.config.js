import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [sveltekit()],
    server: {
        host: '0.0.0.0',
        port: 5173,
        allowedHosts: [
            '.ngrok-free.dev',                 //  autorise tous les sous-domaines ngrok-free.dev
            // 'damon-heptangular-heritablely.ngrok-free.dev', // (optionnel) ton host exact
        ],
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    }

});
