import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';


export function getOrder ({ commit, dispatch }, id) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/order/' + id + '/')
      .then((response) => {
        commit('UPDATE_ENTRY', response.data.order);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getEmptyOrder ({ commit, dispatch }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/order/structure/')
      .then((response) => {
        commit('UPDATE_ENTRY', response.data.order);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getEntries ({ commit, dispatch }, dataType) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + dataType + '/')
      .then((response) => {
        commit('UPDATE_ENTRY_LIST', response.data[dataType + 's']);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function deleteOrder (context, order_id) {
  return new Promise((resolve, reject) => {
    axios
      .delete('/api/v1/order/' + order_id + '/',
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


export function saveOrder (context, payload) {
  return new Promise((resolve, reject) => {
    let uuid = payload.id;
    delete payload.id;
    if (uuid === '') {
      axios
        .post('/api/v1/order/',
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
        .patch('/api/v1/order/' + uuid + '/',
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


export function addDataset (context, payload) {
  return new Promise((resolve, reject) => {
    axios
      .post('/api/v1/order/' + payload.uuid + '/dataset/',
            payload.data,
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


export function setEntryFields({ commit }, data) {
  return new Promise((resolve, reject) => {
    commit('UPDATE_ENTRY_FIELDS', data);
    resolve();
  });
}


export function resetEntryList({ commit }, data) {
  return new Promise((resolve, reject) => {
    commit('RESET_ENTRY_LIST', data);
    resolve();
  });
}
