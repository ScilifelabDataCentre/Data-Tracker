import Vue from 'vue'

import VueSimpleMarkdown from 'vue-simple-markdown'

import App from './App.vue'

import router from './router';
import store from './store';

import '../node_modules/bulma/css/bulma.css';

import 'vue-simple-markdown/dist/vue-simple-markdown.css'

Vue.use(VueSimpleMarkdown);

Vue.config.productionTip = false;

Vue.filter('capitalize', function (value) {
  if (!value) {
    return ''
  }
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
});

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app')
