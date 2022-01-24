import { route } from 'quasar/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (store /* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.MODE === 'ssr' ? void 0 : process.env.VUE_ROUTER_BASE)
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
})
