import axios from 'axios';

export function getDataset ({ commit, dispatch }, id) {
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
}

export function getDatasets ({ commit, dispatch }) {
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
}
