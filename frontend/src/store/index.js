import Vue from 'vue';
import Vuex from 'vuex';

import admin from './modules/admin';
import dataset from './modules/dataset';
import project from './modules/project';
import user from './modules/user';

Vue.use(Vuex);

const state = {
  notification: {'message': '',
                 'type': 'normal'},
}

const mutations = {
  UPDATE_NOTIFICATION (state, payload) {
    state.notification = payload;
  },
}

const actions = {
  updateNotification({ commit }, notification) {
    return new Promise((resolve) => {
      commit('UPDATE_NOTIFICATION', {'message': notification[0],
                                     'type': notification[1]});
      resolve();
    });
  },
}

const getters = {
  notification: state => state.notification,
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  modules: {
    admin,
    dataset,
    project,
    user,
  }
})
