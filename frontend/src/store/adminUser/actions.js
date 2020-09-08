import axios from 'axios'

export function getUsers ({ commit }) {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/user/')
      .then((response) => {
        commit('updateUsers', response.data.users);
        resolve(response);
      })
      .catch(function (err) {
        reject(err);
      });
  });
}

export function getUser(context, payload) {
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
}

export function getPermissionTypes() {
  return new Promise((resolve, reject) => {
    axios
      .get('/api/user/permissions/')
      .then((response) => {
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

export function genApiKey(context, payload) {
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
}

export function saveUser (context, payload) {
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
}

export function deleteUser (context, payload) {
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
}
