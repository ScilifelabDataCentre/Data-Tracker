import axios from 'axios';

import {getCsrfHeader} from '../../helpers.js';

const state = {
  project: {},
  projects: {},
}

const mutations = {
  UPDATE_PROJECT (state, payload) {
    state.project = payload;
  },
  UPDATE_PROJECTS (state, payload) {
    state.projects = payload;
  },
}

const actions = {
  getProject ({ commit, dispatch }, id) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/project/' + id + '/')
        .then((response) => {
          commit('UPDATE_PROJECT', response.data.project);
          resolve(response);
        })
        .catch((err) => {
          dispatch('updateNotification', ['Unable to retrieve project', 'warning'])
          reject(err);
        });
    });
  },

  getProjects ({ commit, dispatch }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/project/')
        .then((response) => {
          commit('UPDATE_PROJECTS', response.data.projects);
          resolve(response);
        })
        .catch((err) => {
          dispatch('updateNotification', ['Unable to retrieve project list', 'warning'])
          reject(err);
      });
    });
  },

  deleteProject (context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .delete('/api/project/' + payload + '/',
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

  saveProject (context, payload) {
    return new Promise((resolve, reject) => {
      let projectUuid = payload.id;
      delete payload.id
      if (projectUuid === -1) {
        axios
          .post('/api/project/',
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
      }
      else {
        axios
          .patch('/api/project/' + projectUuid + '/',
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
      }
    });
  },
}

const getters = {
  project: state => state.project,
  projects: state => state.projects,
}

const projectModule = {
  state,
  mutations,
  actions,
  getters
}

export default projectModule
