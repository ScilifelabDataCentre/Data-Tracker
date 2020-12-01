<template>
<q-page padding>
  <h2>User Settings</h2>

  <q-card class="q-my-md">
    <q-card-section>
      <span class="text-h5">User Data</span>
    </q-card-section>

    <q-card-section>
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
    </q-card-section>
    <q-card-section>
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
    </q-card-section>
    <q-card-section>
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
    </q-card-section>
  </q-card>

  <q-card>
    <q-card-section>
      <span class="text-h5">Permissions</span>
    </q-card-section>
    <q-card-section class="flex text-bold">
      <q-chip square
              color="blue-9"
              text-color="white"
              v-for="perm in currentUser.permissions"
              :key="perm"
              :label="perm" />
    </q-card-section>
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <span class="text-h5">Logs</span>
    </q-card-section>
    <q-card-section>
      <q-btn label="Logs"
             color="primary"
             class="q-mx-sm"
             @click="showLogs = true"/>
      <q-btn label="Actions"
             color="primary"
             class="q-mx-sm"
             @click="showActions = true"/>
    </q-card-section>

    <log-viewer v-model="showLogs"
                dataType="me" />
    <action-viewer v-model="showActions"
                   uuid="me" />
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <span class="text-h5">API Key</span>
    </q-card-section>

    <q-card-section>
      <span class="text-h6">Available Authentication IDs:</span>
      <q-list>
        <q-item v-for="authId in currentUser.authIds"
                :key="authId">
          <q-chip square
                  color="grey-2"
                  :label="authId" />
        </q-item>
      </q-list>
    </q-card-section>

    <q-card-section>
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
    </q-card-section>
  </q-card>
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
      this.$store.dispatch('currentUser/genApiKey')
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
