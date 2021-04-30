<template>
<q-page padding>
  <h2>User Settings</h2>

  <div class="q-my-md">
    <span class="text-h5">User Data</span>
      <q-input outlined
               filled
               stack-label
               label="UUID"
               :value="currentUser._id"
               class="q-my-sm"
               disable />
      <q-input outlined
               filled
               stack-label
               label="Email"
               :value="currentUser.email"
               disable />
      <q-input outlined
               class="q-my-sm"
               label="Name"
               v-model="userData.name"/>
      <q-input outlined
               class="q-my-sm"
               label="Affiliation"
               v-model="userData.affiliation"/>
      <q-input outlined
               class="q-my-sm"
               label="Contact"
               v-model="userData.contact"/>
      <q-input outlined
               class="q-my-sm"
               label="ORCID"
               v-model="userData.orcid"/>
      <q-input outlined
               class="q-my-sm"
               label="URL"
               v-model="userData.url"/>
      <div class="row">
      <q-btn color="positive"
             class="q-mt-md"
             :label="'Save settings'"
             @click="saveSettings"
             :loading="userDataSaveWaiting">
      </q-btn>
        <span v-show="userDataSaveSuccess" class="text-positive q-ml-md q-mt-md self-center">Settings saved</span>
        <span v-show="userDataSaveError" class="text-negative q-ml-md q-mt-md self-center">Failed to save settings</span>
      </div>
  </div>
  <div class="q-my-md">
    <span class="text-h6">Permissions:</span>
    <div class="row">
      <q-chip square
              color="blue-9"
              text-color="white"
              v-for="perm in currentUser.permissions"
              :key="perm"
              :label="perm" />
    </div>
  </div>

  <div class="q-my-md">
    <q-btn label="Logs"
           color="primary"
           class="q-mx-sm"
           @click="showLogs = true"/>
    <q-btn label="Actions"
           color="primary"
           class="q-mx-sm"
           @click="showActions = true"/>

    <log-viewer v-model="showLogs"
                :uuid="currentUser.id"
                dataType="user" />
    <action-viewer v-model="showActions"
                   :uuid="currentUser.id" />
  </div>

  <div class="q-my-md">
      <span class="text-h6">Available Authentication IDs:</span>
      <q-list>
        <q-item v-for="authId in currentUser.authIds"
                :key="authId">
          <q-chip square
                  color="grey-2"
                  :label="authId" />
        </q-item>
      </q-list>

      <div>
      <q-btn color="positive"
             label="Generate new API key"
             :loading="newApiKeyWaiting"
             @click="generateNewApiKey" />
      <span v-if="newApiKeyError" class="text-negative">API key generation failed</span>
      <q-input v-else
               outlined
               stack-label
               v-show="newApiKey.length > 0"
               label="New API Key"
               class="q-my-sm"
               :value="newApiKey"
               disable />
      </div>
  </div>
</q-page>
</template>

<script>
import LogViewer from 'components/LogViewer.vue'
import ActionViewer from 'components/ActionViewer.vue'

export default {
  name: 'CurrentUserInfo',

  computed: {
    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    }
  },

  components: {
    'log-viewer': LogViewer,
    'action-viewer': ActionViewer,
  },
  
  data () {
    return {
      userData: {},
      userDataSaveSuccess: false,
      userDataSaveError: false,
      userDataSaveWaiting: false,
      filter: '',
      pageAbout: '',
      pageNew: '',
      newApiKey: '',
      newApiKeyError: false,
      newApiKeyWaiting: false,
      showActions: false,
      showLogs: false,
    }
  },

  methods: {
    saveSettings () {
      this.userDataSaveSuccess = false;
      this.userDataSaveError = false;
      this.userDataSaveWaiting = true;
      let toSubmit = JSON.parse(JSON.stringify(this.userData));
      delete toSubmit._id;
      this.$store.dispatch('currentUser/updateInfo', toSubmit)
        .then(() => {
          this.$store.dispatch('currentUser/getInfo');
          this.userDataSaveSuccess = true;
          this.userDataSaveWaiting = false;
        })
        .catch(() => {
          this.userDataSaveError = true;
          this.userDataSaveWaiting = false;
        });
    },

    generateNewApiKey () {
      this.newApiKeyWaiting = true;
      this.newApiKeyError  = false;
      this.$store.dispatch('currentUser/genApiKey', this.currentUser.id)
        .then((response) => this.newApiKey = response.data.key)
        .catch(() => this.newApiKeyError = true)
        .finally(() => this.newApiKeyWaiting = false);
    },

    trimUserData () {
      delete this.userData.authIds;
      delete this.userData.email;
      delete this.userData.permissions;
    },
  },

  mounted () {
    this.$store.dispatch('currentUser/getInfo')
      .then(() => {
        this.userData = JSON.parse(JSON.stringify(this.currentUser))
        this.trimUserData();
      });
  },

}
</script>
