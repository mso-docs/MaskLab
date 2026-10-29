import {defineConfig} from 'vite';
export default defineConfig({server:{proxy:{'/api':'http://127.0.0.1:8000'}},build:{outDir:'../src/masklab/static',emptyOutDir:true}});
