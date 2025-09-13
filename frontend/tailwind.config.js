/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'dark-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'purple-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'blue-gradient': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'dark-blue-gradient': 'linear-gradient(135deg, #2c3e50 0%, #3498db 100%)',
        'night-gradient': 'linear-gradient(135deg, #232526 0%, #414345 100%)',
        'cyber-gradient': 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
      },
      colors: {
        'dark-bg': '#0f0f23',
        'dark-surface': '#1a1a2e',
        'dark-accent': '#16213e',
        'neon-blue': '#00f2fe',
        'neon-purple': '#764ba2',
      }
    },
  },
  plugins: [],
}