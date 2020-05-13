import axios from 'axios';

import {getCsrfHeader} from '../../helpers.js';

const state = {
  order: {},
  orders: {},
}

const mutations = {
  UPDATE_ORDER (state, payload) {
    state.order = payload;
  },
  UPDATE_ORDERS (state, payload) {
    state.orders = payload;
  },
}

const actions = {
  getOrder ({ commit, dispatch }, id) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/order/' + id + '/')
        .then((response) => {
          commit('UPDATE_ORDER', response.data.order);
          resolve(response);
        })
        .catch((err) => {
          dispatch('updateNotification', ['Unable to retrieve order', 'warning'])
          reject(err);
        });
    });
  },

  getOrders ({ commit, dispatch }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/order/')
        .then((response) => {
          commit('UPDATE_ORDERS', response.data.orders);
          resolve(response);
        })
        .catch((err) => {
          dispatch('updateNotification', ['Unable to retrieve order list', 'warning'])
          reject(err);
      });
    });
  },

  deleteOrder (context, order_id) {
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
  },

  saveOrder (context, payload) {
    return new Promise((resolve, reject) => {
      let uuid = payload.id;
      delete payload.id;
      payload.creator = payload.creator.id;
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
  },

  addDataset (context, payload) {
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
  },
}

const getters = {
  order: state => state.order,
  orders: state => state.orders,
}

const orderModule = {
  state,
  mutations,
  actions,
  getters
}

export default orderModule
