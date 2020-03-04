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
        .get('/api/project/' + id)
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

  deleteProject (context, project_id) {
    return new Promise((resolve, reject) => {
      axios
        .post('/api/project/delete',
              {
                'id': project_id,
              },
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
      const newProject = {'project': payload};
      let url = '';
      if (newProject.project.id === -1) {
        url = '/api/project/add';
      }
      else {
        url = '/api/project/' + newProject.project.id + '/update';
      }
      axios
        .post(url,
              newProject,
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
