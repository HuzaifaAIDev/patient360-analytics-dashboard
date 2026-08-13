/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["Manrope", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      colors: {
        ink: {
          950: "#0A0E14",
          900: "#0F1520",
          800: "#151C2C",
          700: "#1D2638",
          600: "#2A3550",
        },
        clinical: {
          50: "#EEFBFA",
          100: "#D3F5F1",
          200: "#A7EBE4",
          300: "#6FDBD1",
          400: "#3EC3B7",
          500: "#1FA89C",
          600: "#15877E",
          700: "#146B66",
          800: "#145653",
          900: "#0F3E3C",
        },
        amber: {
          400: "#F5A623",
          500: "#E8940E",
        },
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(15, 62, 60, 0.12)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
