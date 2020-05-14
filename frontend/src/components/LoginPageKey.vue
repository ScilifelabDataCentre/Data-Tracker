<template>
<div class="login-key">
  <h1 class="subtitle is-1"></h1>
  <form @submit="submitLogin">
    <div class="field">
      <input id="username"
             class="input"
             name="USERNAME"
             type="text"
             placeholder="username"
             v-model="loginInfo.apiUser"/>
    </div>
    <div class="field">
      <input id="apikey"
             class="input"
             name="APIKEY"
             type="password"
             placeholder="API key"
             v-model="loginInfo.apiKey"/>
    </div>
    <div class="control">
      <button class="button is-link">Submit</button>
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
    }
  },
  methods: {
    submitLogin(event) {
      event.preventDefault();
      let loginData = {'api-key': this.loginInfo.apiKey,
                       'api-user': this.loginInfo.apiUser}
      this.$store.dispatch('loginKey', loginData)
        .then((response) => {
          // add performed
          let uuid = '';
          if (response.data) {
            uuid = response.data.uuid;
          }
          else {
            uuid = this.newDataset.uuid
          }
          this.$router.push("/dataset/" + uuid + "/about");
        });
    },
  },
}
</script>

<style scoped>

</style>
