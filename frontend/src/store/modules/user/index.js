import axios from 'axios';

import {getCsrfHeader} from '../../helpers.js';

const state = {
  user: {},
  user_datasets: [],
  user_orders: [],
  user_projects: [],
}

const mutations = {
  UPDATE_CURRENT_USER (state, payload) {
    state.user = payload;
  },
  UPDATE_USER_DATASETS (state, payload) {
    state.user_datasets = payload;
  },
  UPDATE_USER_ORDERS (state, payload) {
    state.user_orders = payload;
  },
  UPDATE_USER_PROJECTS (state, payload) {
    state.user_projects = payload;
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

  getUserOrders ({ commit }) {
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

  getUserDatasets ({ commit }) {
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

  getUserProjects ({ commit }) {
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
  user_orders: state => state.user_orders,
  user_datasets: state => state.user_datasets,
  user_projects: state => state.user_projects,
}

const userModule = {
  state,
  mutations,
  actions,
  getters
}

export default userModule
