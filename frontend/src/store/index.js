import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const state = {
  user: {},
}

const mutations = {
  UPDATE_USER (state, payload) {
    state.user = payload;
  },
}

const actions = {
  getUser ({ commit }) {
    axios
      .get('/api/users/me')
      .then((response) => {
        commit('UPDATE_USER', response.data);
      });
  },
}

const getters = {
  user: state => state.user,
}

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
})

export default store
