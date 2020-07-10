import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';

export function getCollection ({ commit, dispatch }, id) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/project/' + id + '/')
      .then((response) => {
        commit('updateCollection', response.data.project);
        resolve(response);
      })
      .catch((err) => {
        commit('updateCollection', {});
        reject(err);
      });
  });
}

export function getCollections ({ commit, dispatch }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/project/')
      .then((response) => {
        commit('updateCollections', response.data.projects);
        resolve(response);
      })
      .catch((err) => {
        commit('updateCollections', []);
        reject(err);
      });
  });
}

export function deleteCollection (context, payload) {
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
}

export function saveCollection (context, payload) {
  return new Promise((resolve, reject) => {
    let projectUuid = payload.id;
    delete payload.id
    if (projectUuid === '-1') {
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
}
