import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';


export function getEntry ({ commit, dispatch }, payload) {
  // payload: {'id': id, 'dataType': dataType}
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + payload.dataType + '/' + payload.id + '/')
      .then((response) => {
        commit('UPDATE_ENTRY', response.data[payload.dataType]);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getEmptyEntry ({ commit, dispatch }, dataType) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/order/structure/')
      .then((response) => {
        commit('UPDATE_ENTRY', response.data[dataType]);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function deleteEntry (context, payload) {
  // payload: {'id': id, 'dataType': dataType}
  return new Promise((resolve, reject) => {
    axios
      .delete('/api/v1/' + payload.dataType + '/' + payload.id + '/',
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


export function saveEntry (context, payload) {
  // payload: {'data': data, 'dataType': dataType}
  return new Promise((resolve, reject) => {
    let uuid = payload.data.id;
    delete payload.data.id;
    if (uuid === '') {
      axios
        .post('/api/v1/' + payload.dataType + '/',
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
    }
    else {
      axios
        .patch('/api/v1/' + payload.dataType + '/' + uuid + '/',
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


// expects payLoad: {'tagName': tagName, 'values': tagObject}
export function setTags({ commit }, payload) {
  return new Promise((resolve, reject) => {
    commit('UPDATE_TAGS', payload);
    resolve();
  });
}

// expects payLoad: {'tagName': tagName, 'value': {key: value}}
export function setTag({ commit }, payload) {
  return new Promise((resolve, reject) => {
    commit('UPDATE_TAG', payload);
    resolve();
  });
}

// expects payLoad: {'tagName': tagName, 'key': keyName}
export function deleteTag({ commit }, payload) {
  return new Promise((resolve, reject) => {
    commit('DELETE_TAG', payload);
    resolve();
  });
}


export function setUserTags({ commit }, data) {
  return new Promise((resolve, reject) => {
    commit('UPDATE_USER_TAGS', data);
    resolve();
  });
}



export function resetEntryList({ commit }) {
  return new Promise((resolve, reject) => {
    commit('RESET_ENTRY_LIST');
    resolve();
  });
}


export function resetEntry({ commit }) {
  return new Promise((resolve, reject) => {
    commit('RESET_ENTRY');
    resolve();
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
