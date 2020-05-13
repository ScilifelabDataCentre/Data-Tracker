import axios from 'axios';

import {getCsrfHeader} from '../../helpers.js';

const state = {
  dataset: {},
  datasets: {},
}

const mutations = {
  UPDATE_DATASET (state, payload) {
    state.dataset = payload;
  },
  UPDATE_DATASETS (state, payload) {
    state.datasets = payload;
  },
}

const actions = {
  getDataset ({ commit, dispatch }, id) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/dataset/' + id + '/')
        .then((response) => {
          commit('UPDATE_DATASET', response.data.dataset);
          resolve(response);
        })
        .catch((err) => {
          dispatch('updateNotification', ['Unable to retrieve dataset', 'warning'])
          reject(err);
        });
    });
  },

  getDatasets ({ commit, dispatch }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/dataset/')
        .then((response) => {
          commit('UPDATE_DATASETS', response.data.datasets);
          resolve(response);
        })
        .catch((err) => {
          dispatch('updateNotification', ['Unable to retrieve dataset list', 'warning'])
          reject(err);
      });
    });
  },

  deleteDataset (context, dataset_id) {
    return new Promise((resolve, reject) => {
      axios
        .delete('/api/dataset/' + dataset_id + '/',
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

  saveDataset (context, payload) {
    return new Promise((resolve, reject) => {
      const newDataset = payload;
      let url = '';
        url = '/api/dataset/' + newDataset.uuid + '/edit/';
      delete newDataset.uuid;
      delete newDataset.identifier;
      delete newDataset.dataUrls;
      axios
        .post(url,
              newDataset,
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
  dataset: state => state.dataset,
  datasets: state => state.datasets,
}

const datasetModule = {
  state,
  mutations,
  actions,
  getters
}

export default datasetModule
