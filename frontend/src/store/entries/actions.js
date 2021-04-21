import axios from 'axios';

import {getCsrfHeader} from '../helpers.js';


export function getEntry ({ commit, dispatch }, payload) {
  // payload: {'id': id, 'dataType': dataType}
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + payload.dataType + '/' + payload.id)
      .then((response) => {
        commit('UPDATE_ENTRY', response.data[payload.dataType]);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getLocalEntry ({ commit, dispatch }, payload) {
  // payload: {'id': id, 'dataType': dataType}
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + payload.dataType + '/' + payload.id)
      .then((response) => {
        resolve(response.data[payload.dataType]);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getEntryLog ({ commit, dispatch }, payload) {
  // payload: {'id': id, 'dataType': dataType}
  return new Promise((resolve, reject) => {
    if (payload.dataType !== 'me') {
      axios
        .get('/api/v1/' + payload.dataType + '/' + payload.id + '/log')
        .then((response) => {
          commit('UPDATE_ENTRY_LOG', response.data.logs);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    }
    else {
      axios
        .get('/api/v1/user/me/log')
        .then((response) => {
          commit('UPDATE_ENTRY_LOG', response.data.logs);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    }
  });
}


export function getUserActions ({ commit, dispatch }, payload) {
  // payload: uuid or 'me'
  return new Promise((resolve, reject) => {
    if (payload !== 'me') {
      axios
        .get('/api/v1/user/' + payload + '/actions')
        .then((response) => {
          commit('UPDATE_USER_ACTIONS', response.data.logs);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    }
    else {
      axios
        .get('/api/v1/user/me/actions')
        .then((response) => {
          commit('UPDATE_USER_ACTIONS', response.data.logs);
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
    }
  });
}


export function getEmptyEntry ({ commit, dispatch }, dataType) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + dataType + '/structure')
      .then((response) => {
        commit('UPDATE_ENTRY', response.data[dataType]);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getLocalEmptyEntry ({ commit, dispatch }, dataType) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + dataType + '/structure')
      .then((response) => {
        resolve(response.data[dataType]);
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
      .delete('/api/v1/' + payload.dataType + '/' + payload.id,
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
        .post('/api/v1/' + payload.dataType,
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
        .patch('/api/v1/' + payload.dataType + '/' + uuid,
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
      .post('/api/v1/order' + payload.uuid + '/dataset',
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


// expects payLoad: {'propertyName': propertyName, 'key': keyName}
export function addProperty({ commit }, payload) {
  return new Promise((resolve, reject) => {
    commit('ADD_PROPERTY', payload);
    resolve();
  });
}


// expects payLoad: {'tagName': tagName, 'value': {key: value}}
export function setProperty({ commit }, payload) {
  return new Promise((resolve, reject) => {
    commit('UPDATE_PROPERTY', payload);
    resolve();
  });
}

// expects payLoad: {'propertyName': propertyName, 'key': keyName}
export function deleteProperty({ commit }, payload) {
  return new Promise((resolve, reject) => {
    commit('DELETE_PROPERTY', payload);
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


export function resetEntryLog({ commit }) {
  return new Promise((resolve, reject) => {
    commit('RESET_ENTRY_LOG');
    resolve();
  });
}


export function resetUserActions({ commit }) {
  return new Promise((resolve, reject) => {
    commit('RESET_USER_ACTIONS');
    resolve();
  });
}


export function getEntries ({ commit, dispatch }, dataType) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + dataType)
      .then((response) => {
        commit('UPDATE_ENTRY_LIST', response.data[dataType + 's']);
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}


export function getLocalEntries ({ commit, dispatch }, dataType) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/v1/' + dataType)
      .then((response) => {
        resolve(response.data[dataType + 's']);
      })
      .catch((err) => {
        reject(err);
      });
  });
}
