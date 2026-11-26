import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: process.env.TEST_DIR || './fixtures', timeout: 15000, expect: { timeout: 3000 }, reporter: 'line', use: { baseURL: 'https://demo.playwright.dev', headless: true } });
