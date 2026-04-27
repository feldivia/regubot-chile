import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f0ff',
          100: '#e0e0ff',
          200: '#c7c4ff',
          300: '#a59eff',
          400: '#8b7cf8',
          500: '#7c5cfc',
          600: '#6d45e8',
          700: '#5b36c4',
          800: '#4b2d9e',
          900: '#3e277e',
        },
      },
    },
  },
  plugins: [],
}

export default config
