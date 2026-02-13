import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import path from 'path'

// https://vite.dev/config/
export default defineConfig({
    build: {
        target: 'esnext',
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@components': path.resolve(__dirname, './src/components'),
            '@pages': path.resolve(__dirname, './src/pages'),
            '@assets': path.resolve(__dirname, './src/assets'),
            '@util': path.resolve(__dirname, './src/util'),
            '@hooks': path.resolve(__dirname, './src/hooks'),
        }
    },
    plugins: [react()],
})
