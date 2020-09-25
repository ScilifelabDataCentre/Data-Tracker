import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';


export function getOrder ({ commit, dispatch }, id) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/order/' + id + '/')
      .then((response) => {
        commit('updateOrder', response.data.order);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function setOrderFields({ commit }, data) {
  commit('updateOrderFields', data);
}

export function getEmptyOrder ({ commit, dispatch }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/order/structure/')
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
      .get('/api/v1/order/')
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
