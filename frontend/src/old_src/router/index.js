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

  function routeChecker (to, from, next) {
    let ruleMatch = false;
    if (to.matched.some(entry => entry.meta.loginRequired)) {
      if (!store.store.getters['currentUser/isLoggedIn']) {
        ruleMatch = true;
        next({name: 'Login', params: {origin: {name: to.name, path: to.path}}});
      }
      else if (to.matched.some(entry => entry.meta.permissionRequired)) {
        let permissions = to.matched.map((entry) => entry.meta.permissionRequired).flat();
        for (let perm of permissions) {
          if (perm === undefined)
            continue;
          if (!store.store.getters['currentUser/info'].permissions.includes(perm)) {
            ruleMatch = true;
            next({name: 'Forbidden', params: {toPath: {name: to.name,
                                                       path: to.path},
                                              fromPath: {name: from.name,
                                                         path: from.path}}});
            break;
          }
        }
      }
    }
    return ruleMatch
  }

  Router.beforeEach((to, from, next) => {
    if (!store.store.getters['currentUser/infoLoaded']) {
      store.store.dispatch('currentUser/getInfo')
        .then(() => { if (!routeChecker(to, from, next)) next() })
        .catch(() => next({name: 'No Backend'}));
    }
    else {
      if (!routeChecker(to, from, next))
        next();
    }
  })
  return Router
}
