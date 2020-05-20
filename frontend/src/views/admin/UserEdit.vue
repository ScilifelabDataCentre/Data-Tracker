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
    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newUser.id != '' && user.permissions.includes('DATA_MANAGEMENT')" @click="deleteUser">Delete</button>
      </div>
      <p v-if="badSubmit" class="help is-danger">Failed to perform action</p>
    </div>
  </form>
  
</div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserEdit',

  props: ['uuid'],

  data () {
    return {
      newUser: {
        id: '',
        name: '',
        email: '',
        affiliation: '',
      },
      badSubmit: false
    }
  },

  created () {
    if (this.uuid) {
      axios
        .get('/api/user/' + this.uuid + '/')
        .then((response) => {
          this.newUser = response.data;
        })
        .catch(() => {
          this.$store.dispatch('updateNotification', ['Failed to get user information', 'warning']);
        });
    }
  },

  methods: {
    saveExtra(event) {
      event.preventDefault();
      if (this.extraKey !== '') {
        if (this.newUser.extra[this.extraKey] !== undefined) {
          if (this.extraValue === '') {
            this.$delete(this.newUser.extra, this.extraKey);
          }
          else {
            this.newUser.extra[this.extraKey] = this.extraValue;
          }
        }
        else {
          if (this.extraValue !== '') {
            this.$set(this.newUser.extra, this.extraKey, this.extraValue);
          }
        }
      }
    },    

    cancelChanges(event) {
      event.preventDefault();
      if (this.newUser.id === -1) {
        this.$router.push("/user/browser");
      }
      else {
        this.$router.push("/user/" + this.newUser.id + "/about");
      }
    },

    deleteUser(event) {
      event.preventDefault();
      this.$store.dispatch('deleteUser', this.newUser.id)
        .then(() => {
          this.$router.push("/user/browser");
        });
    },

    submitUserForm(event) {
      event.preventDefault();
      this.$store.dispatch('saveUser', this.newUser)
        .then((response) => {
          // add performed
          let id = -1;
          if (response.data) {
            id = response.data._id;
          }
          else {
            id = this.$props.uuid;
          }
          this.$router.push("/user/" + id + "/about");
        });
    },
  },
}
</script>

<style scoped>

</style>
