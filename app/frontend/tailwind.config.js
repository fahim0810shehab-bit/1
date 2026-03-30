/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        nsu: {
          primary: "#1a365d",
          secondary: "#2b6cb0",
          accent: "#63b3ed",
          dark: "#0d1b2a",
          light: "#e2e8f0",
          success: "#38a169",
          warning: "#d69e2e",
          danger: "#e53e3e",
        }
      },
      backdropBlur: {
        xs: "2px",
      }
    },
  },
  plugins: [],
}
