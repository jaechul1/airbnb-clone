module.exports = {
  purge: [
    "./templates/**/*.html"
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      spacing: {
        "25vh": "25vh",
        "50vh": "50vh",
        "75vh": "75vh"
      },
      colors: {
        "kakao": "#ffe812",
        "github": "#6e5494"
      }
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
