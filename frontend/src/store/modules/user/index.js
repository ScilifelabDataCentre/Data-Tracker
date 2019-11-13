import axios from 'axios';

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
    return new Promise((resolve, reject) => {
      axios
        .get('/api/users/me')
        .then((response) => {
          commit('UPDATE_USER', response.data);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },
}

const getters = {
  user: state => state.user,
}

const userModule = {
  state,
  mutations,
  actions,
  getters
}

export default userModule
