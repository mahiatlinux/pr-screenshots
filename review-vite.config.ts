import { defineConfig, mergeConfig } from 'vite';
import config from './vite.config';
export default mergeConfig(config, defineConfig({build:{outDir:'review-dist',rollupOptions:{input:'review-ui.html'}},server:{host:'127.0.0.1'}}));
