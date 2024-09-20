/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,jsx}"],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  },
  plugins: [
    require('daisyui'),
  ],
}