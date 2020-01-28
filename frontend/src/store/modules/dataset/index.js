import axios from 'axios';

import {getXsrf} from '../../helpers.js';

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
  getDataset ({ commit }, id) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/dataset/' + id)
        .then((response) => {
          commit('UPDATE_DATASET', response.data.dataset);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },

  getDatasets ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/dataset/all')
        .then((response) => {
          commit('UPDATE_DATASETS', response.data.datasets);
          resolve(response);
        })
      .catch((err) => {
        reject(err);
      });
    });
  },                  

  deleteDataset (context, dataset_id) {
    return new Promise((resolve, reject) => {
      axios
        .post('/api/dataset/delete',
              {
                'id': dataset_id,
              },
              {
                headers: {'X-Xsrftoken': getXsrf()},
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
      if (newDataset.uuid === '') {
        url = '/api/dataset/add';
      }
      else {
        url = '/api/dataset/' + newDataset.uuid + '/edit';
      }
      delete newDataset.uuid;
      delete newDataset.timestamp;
      delete newDataset.identifier;
      delete newDataset.dataUrls;
      axios
        .post(url,
              newDataset,
              {
                headers: {'X-CSRFToken': getXsrf()},
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
