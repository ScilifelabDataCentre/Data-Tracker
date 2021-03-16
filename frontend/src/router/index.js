import Vue from 'vue'
import VueRouter from 'vue-router'

import routes from './routes'

Vue.use(VueRouter)

export default function (store) {
  const Router = new VueRouter({
    scrollBehavior: () => ({ x: 0, y: 0 }),
    routes,

    mode: process.env.VUE_ROUTER_MODE,
    base: process.env.VUE_ROUTER_BASE
  })

  Router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.loginRequired)) {
      if (!store.store.getters['currentUser/infoLoaded']) {
        store.store.dispatch('currentUser/getInfo')
          .then(() => {
            if (!store.store.getters['currentUser/isLoggedIn']) {
              next({name: 'Login', params: {origin: {name: to.name, path: to.path}}});
            }
            else {
              next();
            }
          })
      }
      else {
        next();
      }
    }
    else {
      next();
    }
  })

  return Router
}
