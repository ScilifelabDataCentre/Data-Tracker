import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';

export function getOrder ({ commit, dispatch }, id) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/order/' + id + '/')
      .then((response) => {
        commit('updateOrder', response.data.order);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

export function getOrders ({ commit, dispatch }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/order/')
      .then((response) => {
        commit('updateOrders', response.data.orders);
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
      .delete('/api/order/' + order_id + '/',
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
        .post('/api/order/',
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
        .patch('/api/order/' + uuid + '/',
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
      .post('/api/order/' + payload.uuid + '/dataset/',
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
