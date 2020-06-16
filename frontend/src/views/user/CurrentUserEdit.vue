<template>
<div>
  <h1 class="title is-1">Edit User</h1>
  <form @submit="submitUserForm">
    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <label class="label" for="user-name">Name</label>
      </div>
      <div class="field-body">
        <input class="input"
               id="user-name"
               v-model="newUser.name"
               name="USER_NAME"
               type="text"
               placeholder="Name" />
      </div>
    </div>

    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <label class="label" for="user-affiliation">Affiliation</label>
      </div>
      <div class="field-body">
        <input id="user-affiliation"
               class="input"
               v-model="newUser.affiliation"
               name="USER_AFFILIATION"
               type="text"
               placeholder="A University" />
      </div>
    </div>

    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <span class="label">API key</span>
      </div>
      <div class="field-body">
        <div v-if="newUser.id !== ''" class="field">
          <button class="button is-primary" @click="newApiKey">Generate new</button>
          <div v-if="apiKey !== ''">
            {{ apiKey }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <p v-if="badSubmit" class="help is-danger">Failed to perform action</p>
    </div>
  </form>
  
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'CurrentUserEdit',

  computed: {
    ...mapGetters(['user']),
  },
  
  data () {
    return {
      newUser: {
        name: '',
        affiliation: '',
      },
      apiKey: '',
      badSubmit: false,
      permissionTypes: [],
      currentPermissions: {}
    }
  },

  created () {
    this.$store.dispatch('getCurrentUser', this.uuid)
      .then(() => {
        this.newUser.name = this.user.name;
        this.newUser.affiliation = this.user.affiliation;
      });
  },

  methods: {
    newApiKey(event) {
      event.preventDefault();
      this.$store.dispatch('genApiKeyCurrentUser')
        .then((response) => {
          this.apiKey = response.data.key;
        })
        .catch(() => {
        });
    },

    cancelChanges(event) {
      event.preventDefault();
      this.$router.push("/user/about");
    },

    submitUserForm(event) {
      event.preventDefault();
      this.$store.dispatch('updateCurrentUser', this.newUser)
        .then(() => {
          this.$router.push("/user/about");
        });
    },
  },
}
</script>
