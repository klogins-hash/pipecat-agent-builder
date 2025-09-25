/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@pipecat-ai/voice-ui-kit/dist/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist Variable', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono Variable', 'monospace'],
      },
    },
  },
  plugins: [],
}
