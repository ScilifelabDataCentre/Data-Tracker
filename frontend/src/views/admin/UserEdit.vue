<template>
<div>
  <h1 class="title is-1">Edit User</h1>
  <form @submit="submitUserForm">
    <div class="field is-horizontal" v-if="newUser.id !== ''">
      <div class="field-label is-normal">
        <label for="user-id" class="label">Identifier</label>
      </div>
      <div class="field-body">
        <input id="user-id"
               class="input"
               name="USER_ID"
               type="text"
               placeholder=""
               v-model="newUser.id"
               disabled="true"/>
      </div>
    </div>

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
        <label class="label" for="user-auth">Authentication ID</label>
      </div>
      <div class="field-body">
        <input class="input"
               id="user-auth"
               v-model="newUser.authId"
               name="USER_AUTH"
               type="text"
               placeholder="username@entity" />
      </div>
    </div>

    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <label class="label" for="user-email">Email</label>
      </div>
      <div class="field-body">
        <input id="user-email"
               class="input"
               v-model="newUser.email"
               name="USER_EMAIL"
               type="text"
               placeholder="email@example.com" />
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

    <div class="field is-horizontal">
      <div class="field-label is-normal">
        <span class="label">Permissions</span>
      </div>
      <div class="field-body">
        <div class="field">
          <div class="control" v-for="permission in Object.keys(currentPermissions)" :key="permission">
            <label class="checkbox">
              <input type="checkbox" v-model="currentPermissions[permission]"> {{ permission }}
            </label>
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
      <div class="control">
        <button class="button is-danger" v-if="newUser.id !== ''" @click="deleteUser">Delete</button>
      </div>
      <p v-if="badSubmit" class="help is-danger">Action failed</p>
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
      badSubmit: false,
      permissionTypes: [],
      currentPermissions: {}
    }
  },

  created () {
    this.$store.dispatch('getPermissionTypes')
      .then((response) => {
        response.data.permissions.forEach((permission) => {
          this.$set(this.currentPermissions, permission, false);
        });
        if (this.uuid) {
          this.$store.dispatch('getUser', this.uuid)
            .then((response) => {
              this.newUser = response.data.user;
              delete this.newUser.apiKey;
              delete this.newUser.apiSalt;
              this.newUser.id = this.newUser._id;
              delete this.newUser._id;
              this.newUser.permissions.forEach((permission) => {
                this.currentPermissions[permission] = true;
              });
            });
        }
      });
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
      this.$router.push("../list");
    },

    deleteUser(event) {
      event.preventDefault();
      this.$store.dispatch('deleteUser', this.newUser.id)
        .then(() => {
          this.$router.push("../list");
        });
    },

    submitUserForm(event) {
      event.preventDefault();
      let newData = this.newUser;
      newData.auth_id = newData.authId;
      delete newData.authId;
      newData.permissions = [];
      Object.keys(this.currentPermissions).forEach((permission) => {
        if (this.currentPermissions[permission]) {
          newData.permissions.push(permission);
        }
      });
      this.$store.dispatch('saveUser', newData)
        .then(() => {
          this.$router.push("../list");
        });
    },
  },
}
</script>
