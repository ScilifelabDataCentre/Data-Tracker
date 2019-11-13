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
          commit('UPDATE_DATASET', response.data);
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
        .get('/api/datasets')
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
      const newDataset = {'dataset': payload};
      let url = '';
      if (newDataset.dataset.id === -1) {
        url = '/api/dataset/add';
      }
      else {
        url = '/api/dataset/' + newDataset.dataset.id + '/update';
      }
      axios
        .post(url,
              newDataset,
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
