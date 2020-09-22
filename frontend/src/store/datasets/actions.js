import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';

export function getDataset ({ commit, dispatch }, id) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/dataset/' + id + '/')
      .then((response) => {
        commit('updateDataset', response.data.dataset);
        resolve(response);
      })
      .catch((err) => {
        dispatch('updateNotification', ['Unable to retrieve dataset', 'warning'])
        reject(err);
      });
  });
}

export function getDatasets ({ commit, dispatch }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/dataset/')
      .then((response) => {
        commit('updateDatasets', response.data.datasets);
        resolve(response);
      })
      .catch((err) => {
        dispatch('updateNotification', ['Unable to retrieve dataset list', 'warning'])
        reject(err);
      });
  });
}

export function saveDataset (context, payload) {
  return new Promise((resolve, reject) => {
    let datasetUuid = payload.id;
    delete payload.id;
    axios
      .patch('/api/v1/dataset/' + datasetUuid + '/',
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
}

export function deleteDataset (context, dataset_id) {
  return new Promise((resolve, reject) => {
    axios
      .delete('/api/v1/dataset/' + dataset_id + '/',
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
}
