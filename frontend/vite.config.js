import { defineConfig } from "vite";
import react from "@vitejs/plugin-react"; // Add React plugin
import tailwind from "tailwindcss";
import autoprefixer from "autoprefixer";
import path from "path"; // Add path module

export default defineConfig({
  plugins: [react()], // Use React plugin
  css: {
    postcss: {
      plugins: [tailwind, autoprefixer],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"), // Add path alias
    },
  },
});
