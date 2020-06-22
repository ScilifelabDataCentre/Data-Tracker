import Vue from 'vue'

import VueSimpleMarkdown from 'vue-simple-markdown'

import App from './App.vue'

import router from './router';
import store from './store';

import '../node_modules/bulma/css/bulma.css';

import 'vue-simple-markdown/dist/vue-simple-markdown.css'

Vue.use(VueSimpleMarkdown)

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app')
