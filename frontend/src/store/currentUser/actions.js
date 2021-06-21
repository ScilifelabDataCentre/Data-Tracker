import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';

export function getInfo ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/user/me')
      .then((response) => {
        commit('setInfo', response.data.user);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

export function updateInfo(context, payload) {
  return axios.patch('/api/v1/user/me',
                     {'user': payload},
                     {
                       headers: getCsrfHeader(),
                     });
}
  
export function genApiKey(context, payload) {
  return axios.post('/api/v1/user/' + payload + '/apikey',
                    {},
                    {
                      headers: getCsrfHeader(),
                    });
}
  
export function loginKey (context, payload) {
  return new Promise((resolve, reject) => {
    axios
      .post('/api/v1/login/apikey',
            payload,
            {
              headers: getCsrfHeader(),
            })
      .then((response) => {
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

export function logOut (context) {
  return axios.get('/api/v1/logout')
}

export function getOrders ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/order/user')
      .then((response) => {
        commit('setOrders', response.data.orders);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

export function getDatasets ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/dataset/user')
      .then((response) => {
        commit('setDatasets', response.data.datasets);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

export function getCollections ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/project/user')
      .then((response) => {
        commit('setCollections', response.data.collections);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getOIDC () {
  return axios
    .get('/api/v1/login/oidc')
}
