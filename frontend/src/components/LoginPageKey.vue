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
             v-model="loginInfo.apiUsername"/>
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
        'apiUsername': '',
        'apiKey': '',
      },
    }
  },
  methods: {
    submitLogin(event) {
      event.preventDefault();
      this.$store.dispatch('loginKey', this.loginInfo)
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
