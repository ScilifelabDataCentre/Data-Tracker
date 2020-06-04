<template>
<div>
  <form @submit="submitUserForm">
    <div class="field" v-if="newUser.id !== ''">
      <label for="user-id" class="label">Identifier</label>
      <div class="control">
        <input id="user-id"
               class="input"
               name="USER_ID"
               type="text"
               placeholder=""
               v-model="newUser.id"
               disabled="true"/>
      </div>
    </div>

    <div class="field">
      <label class="label" for="user-name">Name</label>
      <input class="input"
             id="user-name"
             v-model="newUser.name"
             name="USER_NAME"
             type="text"
             placeholder="Name" />
    </div>

    <div class="field">
      <label class="label" for="user-auth">Authentication ID</label>
      <input class="input"
             id="user-auth"
             v-model="newUser.authId"
             name="USER_AUTH"
             type="text"
             placeholder="username@entity" />
    </div>

    <div class="field">
      <label class="label" for="user-email">Email</label>
      <input id="user-email"
             class="input"
             v-model="newUser.email"
             name="USER_EMAIL"
             type="text"
             placeholder="email@example.com" />
    </div>

    <div class="field">
      <label class="label" for="user-affiliation">Affiliation</label>
      <input id="user-affiliation"
             class="input"
             v-model="newUser.affiliation"
             name="USER_AFFILIATION"
             type="text"
             placeholder="A University" />
    </div>

    <div v-if="newUser.id !== ''" class="field">
      <button class="button is-primary" @click="newApiKey">Generate new API key</button>
      <div v-if="apiKey !== ''">
        {{ apiKey }}
      </div>
    </div>
    
    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newUser.id !== ''" @click="deleteUser">Delete</button>
      </div>
      <p v-if="badSubmit" class="help is-danger">Failed to perform action</p>
    </div>
  </form>
  
</div>
</template>

<script>
export default {
  name: 'UserEdit',

  props: ['uuid'],

  data () {
    return {
      newUser: {
        id: '',
        name: '',
        authId: '',
        email: '',
        affiliation: '',
      },
      apiKey: '',
      badSubmit: false
    }
  },

  created () {
    if (this.uuid) {
      console.log('uuid: ' + this.uuid);
      this.$store.dispatch('getUser', this.uuid)
        .then((response) => {
          this.newUser = response.data.user;
          delete this.newUser.apiKey;
          delete this.newUser.apiSalt;
          this.newUser.id = this.newUser._id;
          delete this.newUser._id;
        });
    }
  },

  methods: {
    newApiKey(event) {
      event.preventDefault();
      this.$store.dispatch('genApiKey', this.newUser.id)
        .then((response) => {
          this.apiKey = response.data.key;
        })
        .catch(() => {
        });
    },

    cancelChanges(event) {
      event.preventDefault();
      this.$router.push("/admin/user");
    },

    deleteUser(event) {
      event.preventDefault();
      this.$store.dispatch('deleteUser', this.newUser.id)
        .then(() => {
          this.$router.push("/admin/user");
        });
    },

    submitUserForm(event) {
      event.preventDefault();
      let newData = this.newUser;
      newData.auth_id = newData.authId;
      delete newData.authId;
      this.$store.dispatch('saveUser', newData)
        .then(() => {
          this.$router.push("/admin/user");
        });
    },
  },
}
</script>

<style scoped>

</style>
