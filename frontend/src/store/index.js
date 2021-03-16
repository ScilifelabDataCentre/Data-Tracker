import Vue from 'vue'
import Vuex from 'vuex'

import adminUsers from './adminUsers'
import collections from './collections'
import currentUser from './currentUser'
import datasets from './datasets'
import entries from './entries'

Vue.use(Vuex)

export default function () {
  const Store = new Vuex.Store({
    modules: {
      adminUsers,
      collections,
      currentUser,
      datasets,
      entries,
    },

    strict: process.env.DEV
  })

  return Store
}
