import axios from 'axios';

export function getInfo ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/user/me/')
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
  return new Promise((resolve, reject) => {
    axios
      .patch('/api/user/me/',
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
  
export function genApiKey() {
  return new Promise((resolve, reject) => {
    axios
      .post('/api/user/me/apikey/',
            {},
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
  
export function loginKey (context, payload) {
  return new Promise((resolve, reject) => {
    axios
      .post('/api/login/apikey/',
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

export function getOrders ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/order/user/')
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
      .get('/api/dataset/user/')
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
      .get('/api/project/user/')
      .then((response) => {
        commit('setCollections', response.data.collections);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}
