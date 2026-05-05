import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import path from 'path'
import { fileURLToPath } from 'url'

// Recreate __dirname for ESM config files.
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const base = process.env.VITE_BASE_PATH || '/'
if (!base.startsWith('/') || !base.endsWith('/')) {
    throw new Error(`VITE_BASE_PATH must start and end with "/", got: ${base}`)
}

// https://vite.dev/config/
export default defineConfig({
    base,
    build: {
        target: 'esnext',
    },
    server: {
        proxy: {
            '/api': {
                target: process.env.VITE_API_ORIGIN || 'http://localhost:8000',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
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
