<template>
<div class="login-key">
  <h1 class="subtitle is-1"></h1>
  <form @submit="submitLogin">
    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <label class="label" for="apikey">User</label>
      </div>
      <div class="field-body">
        <input id="username"
               :class="{input: true, 'is-danger': badLogin}"
               name="USERNAME"
               type="text"
               placeholder="username"
               v-model="loginInfo.apiUser"/>
      </div>
    </div>
    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <label class="label" for="apikey">API Key</label>
      </div>
      <div class="field-body">
        <input id="apikey"
               :class="{input: true, 'is-danger': badLogin}"
               name="APIKEY"
               type="password"
               placeholder="API key"
               v-model="loginInfo.apiKey"/>
      </div>
    </div>
    <div class="field is-horizontal">
      <div class="field-label is-normal">
      </div>
      <div class="field-body">
        <div class="control">
          <button class="button is-link">Submit</button>
          <p v-if="badLogin" class="help is-danger">Bad credentials</p>
        </div>
      </div>
    </div>
  </form>
</div>
</template>

<script>
export default {
  name: 'LoginPageKey',
  data () {
    return {
      loginInfo: {
        'apiUser': '',
        'apiKey': '',
      },
      badLogin: false,
    }
  },
  methods: {
    submitLogin(event) {
      event.preventDefault();
      let loginData = {'api-key': this.loginInfo.apiKey,
                       'api-user': this.loginInfo.apiUser}
      this.$store.dispatch('loginKey', loginData)
        .then(() => {
          this.$router.push("/");
          this.$store.dispatch('getCurrentUser');
        })
        .catch(() => {
          this.$store.dispatch('updateNotification', ['Bad login credentials', 'warning']);
          this.badLogin = true;
        });
    },
  },
}
</script>

<style scoped>

</style>
