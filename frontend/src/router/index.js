import Vue from 'vue'
import VueRouter from 'vue-router'

import routes from './routes'

Vue.use(VueRouter)

import { Cookies } from 'quasar'

export default function (store /*, ssrContext } */) {
  const Router = new VueRouter({
    scrollBehavior: () => ({ x: 0, y: 0 }),
    routes,

    mode: process.env.VUE_ROUTER_MODE,
    base: process.env.VUE_ROUTER_BASE
  })

  Router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.loginRequired)) {
      if (!store.store.getters['currentUser/infoLoaded']) {
        console.log('data not loaded');
        console.log(store.store);
        store.store.dispatch('currentUser/getInfo')
          .then(() => {
            console.log('data loaded');
            console.log(store.store);
            if (!store.store.getters['currentUser/isLoggedIn']) {
              console.log('ld, not logged in');
              next({name: 'Login', params: {origin: {name: to.name, path: to.path}}});
            }
            else {
              console.log('ld, logged in');
              next();
            }
          })
      }
      else {
        console.log('logged in');
        next();
      }
    }
    else {
      console.log('default goto next')
      next();
    }
  })

  return Router
}
