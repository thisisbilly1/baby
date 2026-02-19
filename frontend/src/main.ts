import { createApp } from "vue";
// import { createPinia } from "pinia";
import App from "./App.vue";

// Vuetify
import vuetify from "./plugins/vuetify";
import { loadFonts } from "./plugins/webfontloader";

loadFonts();

const app = createApp(App);
app.use(vuetify);
// app.use(createPinia());
app.mount("#app");
