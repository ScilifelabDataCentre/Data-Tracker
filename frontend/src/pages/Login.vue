<template>
<q-page padding>
  <h1 class="text-h2">Login</h1>
  <q-card shadowed
          class="q-my-lg">
    <q-card-section>
      <div class="text-h4">OpenID</div>
    </q-card-section>
    <q-card-section>
      <q-btn type="a"
             class="text-capitalize"
             v-for="authName in Object.keys(oidcTypes)"
             :key="authName"
             :href="oidcTypes[authName]"
             :label="authName">
      </q-btn>
    </q-card-section>
  </q-card>

  <q-card shadowed>
    <q-card-section>
      <div class="text-h4">API Key</div>
    </q-card-section>
    <q-card-section>
      <q-input id="username"
               label="Authentication ID"
               v-model="loginInfo.apiUser">
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
      </q-input>
      <q-input id="apikey"
               label="API Key"
               type="password"
               v-model="loginInfo.apiKey">
        <template v-slot:prepend>
          <q-icon name="vpn_key" />
        </template>
      </q-input>
    </q-card-section>
    <q-card-section>
      <q-btn label="Submit"
             @click="submitLogin" />
      <p v-if="badLogin" class="text-caption text-negative">Bad login credentials</p>
    </q-card-section>
  </q-card>
</q-page>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginPage',

  data() {
    return {
      'oidcTypes': {},
      'loginInfo': {
        'apiUser': '',
        'apiKey': '',
      },
      'badLogin': false,
    }
  },

  methods: {
    submitLogin(event) {
      event.preventDefault();
      let loginData = {'api-key': this.loginInfo.apiKey,
                       'api-user': this.loginInfo.apiUser};
      this.$store.dispatch('currentUser/loginKey', loginData)
        .then(() => {
          this.$router.push("/");
          this.$store.dispatch('currentUser/getInfo');
        })
        .catch(() => {
          this.badLogin = true;
        });
    },
  },

  created () {
    axios
      .get('/api/login/oidc/')
      .then((response) => {
        this.oidcTypes = response.data;
      });
  },

}
</script>
