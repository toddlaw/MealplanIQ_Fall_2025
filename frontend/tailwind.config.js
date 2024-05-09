/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    colors: {
      primary: {
        light: "#c4d2b7",
        DEFAULT: "#88a56f",
        strong: "#66a530",
      },
      secondary: {
        light: "#f2f2f2",
        DEFAULT: "#4e76a5",
        strong: "#3a6ba5",
      },
      white: {
        light: "#f9f9f9",
        DEFAULT: "#ffffff",
      },
      background: {
        light: "#f9f9f9",
        DEFAULT: "#ffffff",
        success: "#ecffee",
        info: "#c6e2ff",
        warning: "#fff3b3",
        error: "#f6d3d1",
      },
      text: {
        DEFAULT: "#88a56f",
        success: "#00B112",
        info: "#48a2ff",
        warning: "#F0754F",
        error: "#F02417",
      },
    },
    extend: {},
  },
  plugins: [],
};
