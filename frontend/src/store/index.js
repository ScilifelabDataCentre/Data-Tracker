import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

function getXsrf() {
  let name = "_xsrf=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

const state = {
  user: {},
  users: {},
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
  UPDATE_USERS (state, payload) {
    state.users = payload;
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
    return new Promise((resolve, reject) => {
      axios
        .get('/api/project/' + id)
        .then((response) => {
          commit('UPDATE_PROJECT', response.data);
          resolve(response);
        })
        .catch(function (err) {
          commit('UPDATE_ERRORS', err);
          reject(err);
        });
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
  getUsers ({ commit }) {
    axios
      .get('/api/users')
      .then((response) => {
        commit('UPDATE_USERS', response.data.users);
      })
      .catch(function (err) {
        commit('UPDATE_ERRORS', err);
      });
  },
  saveProject (context, payload) {
    return new Promise((resolve, reject) => {
      const newProject = {'project': payload};
      state.tmp=axios;
      axios
        .post('/api/project/' + newProject.project.id + '/update',
              newProject,
             {
               headers: {'X-Xsrftoken': getXsrf()},
             })
        .then((response) => {
          resolve(response);
        })
        .catch(function (err) {
          context.commit('UPDATE_ERRORS', err);
          reject(err);
        });
    });
  }
}

const getters = {
  user: state => state.user,
  users: state => state.users,
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
