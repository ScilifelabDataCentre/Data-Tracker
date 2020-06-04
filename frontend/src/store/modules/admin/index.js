import axios from 'axios';

import {getCsrfHeader} from '../../helpers.js';

const state = {
  users: [],
}

const mutations = {
  UPDATE_USERS (state, payload) {
    state.users = payload;
  },
}

const actions = {
  getUsers ({ commit }) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/user/')
        .then((response) => {
          commit('UPDATE_USERS', response.data.users);
          resolve(response);
        })
      .catch(function (err) {
        reject(err);
      });
    });
  },

  getUser(context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .get('/api/user/' + payload + '/')
        .then((response) => {
          resolve(response);
        })
        .catch((err) => {
          this.$store.dispatch('updateNotification', ['Failed to get user information', 'warning']);
          reject(err);
        });
    });
  },

  genApiKey(context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .post('/api/user/' + payload + '/apikey/',
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
  },


  saveUser (context, payload) {
    return new Promise((resolve, reject) => {
      let uuid = payload.id;
      delete payload.id;
      if (uuid === '') {
        axios
          .post('/api/user/',
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
          .patch('/api/user/' + uuid + '/',
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

  deleteUser (context, payload) {
    return new Promise((resolve, reject) => {
      axios
        .delete('/api/user/' + payload +'/',
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
  users: state => state.users,
}

const adminModule = {
  state,
  mutations,
  actions,
  getters,
}

export default adminModule
