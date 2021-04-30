import Vue from 'vue'
import Vuex from 'vuex'

import adminUsers from './adminUsers'
import currentUser from './currentUser'
import entries from './entries'

Vue.use(Vuex)

export default function () {
  const Store = new Vuex.Store({
    modules: {
      adminUsers,
      currentUser,
      entries,
    },

    strict: process.env.DEV
  })

  return Store
}
