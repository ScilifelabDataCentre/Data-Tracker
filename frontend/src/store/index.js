import Vue from 'vue';
import Vuex from 'vuex';

import admin from './modules/admin';
import dataset from './modules/dataset';
import project from './modules/project';
import user from './modules/user';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    admin,
    dataset,
    project,
    user,
  }
})
