import axios from 'axios';

import {getCsrfHeader} from '../../helpers.js';

const state = {
  user: {},
  userDatasets: [],
  userOrders: [],
  userProjects: [],
}

const mutations = {
  UPDATE_CURRENT_USER (state, payload) {
    state.user = payload;
  },
  UPDATE_USER_DATASETS (state, payload) {
    state.userDatasets = payload;
  },
  UPDATE_USER_ORDERS (state, payload) {
    state.userOrders = payload;
  },
  UPDATE_USER_PROJECTS (state, payload) {
    state.userProjects = payload;
  },
}

const actions = {
  getCurrentUser ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/user/me/')
        .then((response) => {
          commit('UPDATE_CURRENT_USER', response.data.user);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },

  updateCurrentUser(context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .patch('/api/user/me/',
               payload,
               {
                 headers: getCsrfHeader(),
               })
        .then((response) => {
          resolve(response);
        })
        .catch(function (err) {
          reject(err);
        });
    });
  },
  
  genApiKeyCurrentUser() {
    return new Promise((resolve, reject) => {
      axios
        .post('/api/user/me/apikey/',
              {},
              {
                headers: getCsrfHeader(),
              })
        .then((response) => {
          resolve(response);
        })
        .catch(function (err) {
          reject(err);
        });
    });
  },
  
  loginKey (context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .post('/api/user/login/apikey/',
              payload,
              {
                headers: getCsrfHeader(),
              })
        .then((response) => {
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },

  getCurrentUserOrders ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/order/user/')
        .then((response) => {
          commit('UPDATE_USER_ORDERS', response.data.orders);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },

  getCurrentUserDatasets ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/dataset/user/')
        .then((response) => {
          commit('UPDATE_USER_DATASETS', response.data.datasets);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },

  getCurrentUserProjects ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/project/user/')
        .then((response) => {
          commit('UPDATE_USER_PROJECTS', response.data.projects);
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
  userOrders: state => state.userOrders,
  userDatasets: state => state.userDatasets,
  userProjects: state => state.userProjects,
}

const userModule = {
  state,
  mutations,
  actions,
  getters
}

export default userModule
