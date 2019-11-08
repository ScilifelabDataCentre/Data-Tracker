import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const state = {
  user: {},
  project: {},
  projects: {},
  dataset: {},
  datasets: {},
  errorCode: undefined,
  errorText: undefined,
}

const mutations = {
  UPDATE_USER (state, payload) {
    state.user = payload;
  },
  UPDATE_DATASET (state, payload) {
    state.dataset = payload;
  },
  UPDATE_DATASETS (state, payload) {
    state.datasets = payload;
  },
  UPDATE_PROJECT (state, payload) {
    state.project = payload;
  },
  UPDATE_PROJECTS (state, payload) {
    state.projects = payload;
  },
  UPDATE_ERRORS (state, payload) {
    state.errorCode = payload.status;
    state.errorText = payload.statusText;
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
  getDataset ({ commit }, id) {
    axios
      .get('/api/dataset/' + id)
      .then((response) => {
        commit('UPDATE_DATASET', response.data);
      })
      .catch(function (err) {
        commit('UPDATE_ERRORS', err);
      });
  },
  getDatasets ({ commit }) {
    axios
      .get('/api/datasets')
      .then((response) => {
        commit('UPDATE_DATASETS', response.data.datasets);
      })
      .catch(function (err) {
        commit('UPDATE_ERRORS', err);
      });
  },
  getProject ({ commit }, id) {
    axios
      .get('/api/project/' + id)
      .then((response) => {
        commit('UPDATE_PROJECT', response.data);
      })
      .catch(function (err) {
        commit('UPDATE_ERRORS', err);
      });
  },
  getProjects ({ commit }) {
    axios
      .get('/api/projects')
      .then((response) => {
        commit('UPDATE_PROJECTS', response.data.projects);
      })
      .catch(function (err) {
        commit('UPDATE_ERRORS', err);
      });
  },
}

const getters = {
  user: state => state.user,
  dataset: state => state.dataset,
  datasets: state => state.datasets,
  project: state => state.project,
  projects: state => state.projects,
  errorCode: state => state.errorCode,
  errorText: state => state.errorText,
}

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
})

export default store
