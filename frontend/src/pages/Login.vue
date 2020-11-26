<template>
<q-page padding>
  <h1 class="text-h2">Login</h1>
  <q-banner v-show="oidcError"
            class="bg-negative text-white q-my-md">
    <template v-slot:avatar>
      <q-icon name="warning" color="white" />
    </template>
    Failed to load the list of supported OpenID Connect logins.
    <template v-slot:action>
      <q-btn flat color="white" label="Dismiss" @click="oidcError=false" />
    </template>
  </q-banner>
  <q-card class="q-my-lg"
          v-show="Object.keys(oidcTypes).length > 0">
    <q-card-section>
      <div class="text-h4">OpenID</div>
    </q-card-section>
    <q-card-section>
      <q-list>
        <q-item v-for="authName in Object.keys(oidcTypes)"
                :key="authName">
          <q-btn type="a"
                 class="text-capitalize"
                 :href="oidcTypes[authName] + '?origin=' + origin.path"
                 :label="authName"
                 color="primary">
          </q-btn>
        </q-item>
      </q-list>
    </q-card-section>
  </q-card>

  <q-card>
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
             @click="submitKeyLogin"
             color="primary"/>
      <p v-show="badKeyLogin" class="text-caption text-negative">Bad login credentials</p>
    </q-card-section>
  </q-card>
</q-page>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginPage',

  props: {
    origin: {
      type: Object,
      default () {
        return {name: 'Home', path: '/'}
      }
    },
  },

  data() {
    return {
      'oidcTypes': {},
      'loginInfo': {
        'apiUser': '',
        'apiKey': '',
      },
      'badKeyLogin': false,
      'badOidcLogin': false,
      'oidcLoading': true,
      'oidcError': false,
    }
  },

  methods: {
    attemptOidcLogin(endpoint) {
      axios.get(endpoint)
        .then(() => {
          this.$router.push({name: this.origin.name});
          this.$store.dispatch('currentUser/getInfo');
        })
        .catch(() => {
          this.badOidcLogin = true;
        });
    },

    submitKeyLogin(event) {
      event.preventDefault();
      let loginData = {'api-key': this.loginInfo.apiKey,
                       'api-user': this.loginInfo.apiUser};
      this.$store.dispatch('currentUser/loginKey', loginData)
        .then(() => {
          this.$router.push({name: this.origin.name});
          this.$store.dispatch('currentUser/getInfo');
        })
        .catch(() => {
          this.badKeyLogin = true;
        });
    },
  },

  created () {
    this.$store.dispatch('currentUser/getOIDC')
      .then((response) => {
        this.oidcTypes = response.data;
        this.oidcLoading = false;
      })
      .catch(() => {
        this.oidcError = true;
        this.oidcLoading = false;
      });
  },

}
</script>
