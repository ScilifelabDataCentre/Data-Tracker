import axios from 'axios';

const state = {
  users: [],
}

const mutations = {
  UPDATE_USERS (state, payload) {
    state.users = payload;
  },
}

const actions = {
  getUsers ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/user/')
        .then((response) => {
          commit('UPDATE_USERS', response.data.users);
          resolve(response);
        })
      .catch(function (err) {
        reject(err);
      });
    });
  },
}

const getters = {
  users: state => state.users,
}

const adminModule = {
  state,
  mutations,
  actions,
  getters,
}

export default adminModule
