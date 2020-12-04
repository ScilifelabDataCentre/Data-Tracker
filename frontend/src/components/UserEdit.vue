<template>
<q-dialog :value="value"
          @input="updateVisibility">
  <q-card v-if="loadingError">
    <q-card-section class="row items-center">
      <q-avatar icon="fas fa-exclamation-triangle" text-color="red" />
      <span class="q-ml-sm">Failed to retrieve user data</span>
    </q-card-section>
    <q-card-actions align="right">
      <q-btn flat label="Ok" color="primary" v-close-popup />
    </q-card-actions>
  </q-card>

  <q-card v-else
          style="width: 400em">
    <q-card-section>
      <q-list>
        <q-item v-show="uuid !== ''">
          <q-item-section>
            <q-input outlined
                     filled
                     stack-label
                     label="UUID"
                     v-model="userData._id"
                     disable />
          </q-item-section>
        </q-item>
        <q-item-label caption>User Data</q-item-label>
        <q-item>
          <q-item-section>
            <q-input outlined
                     label="Email"
                     v-model="userData.email" />
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-input outlined
                     label="Name"
                     v-model="userData.name"/>
            </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-input outlined
                     label="Affiliation"
                     v-model="userData.affiliation"/>
            </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-input outlined
                     label="Contact"
                     v-model="userData.contact"/>
            </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-input outlined
                     label="ORCID"
                     v-model="userData.orcid"/>
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-input outlined
                     label="URL"
                     v-model="userData.url"/>
            </q-item-section>
        </q-item>
        <div v-if="currentUser.permissions.includes('USER_MANAGEMENT')">
          <q-item-label caption>Permissions</q-item-label>
          <div>
            <q-item v-for="field of Object.keys(permissions)"
                    :key="field">
              <q-item-section>
                <q-checkbox v-model="permissions[field]"
                            :label="field" />
              </q-item-section>
            </q-item>
            <q-inner-loading :showing="isLoadingPermissions">
              <q-spinner-dots size="md" color="primary" />
            </q-inner-loading>
          </div>
          <div v-if="uuid !== ''">
            <q-item-label caption>Authentication IDs</q-item-label>
            <q-item class="flex">
              <q-chip v-for="authId in userData.authIds"
                      :key="authId"
                      :label="authId"
                      color="grey-2"
                      square />
            </q-item>
            <q-item-label caption>API Key</q-item-label>
            <q-item>
              <q-item-section>
                <q-btn color="positive"
                       label="Generate new API key"
                       :loading="newApiKeyWaiting"
                       @click="generateNewApiKey" />
                <span class="text-italic text-grey-8">API keys are generated immediately and cannot be reverted</span>
                <q-input outlined
                         stack-label
                         v-show="newApiKey.length > 0"
                         label="New API Key"
                         class="q-my-sm"
                         :value="newApiKey"
                         disable />
              </q-item-section>
            </q-item>
          </div>
        </div>
      </q-list>
    </q-card-section>

    <q-card-section v-if="currentUser.permissions.includes('USER_MANAGEMENT') && uuid !==''">
      <q-btn label="Logs"
             color="primary"
             class="q-mx-sm"
             @click="showLogs = true"/>
      <q-btn label="Actions"
             color="primary"
             class="q-mx-sm"
             @click="showActions = true"/>
      <log-viewer v-model="showLogs"
                  dataType="user"
                  :uuid="uuid"/>
      <action-viewer v-model="showActions"
                     :uuid="uuid" />
    </q-card-section>

    <q-card-actions align="right">
      <span v-show="userDataSaveError" class="text-negative">Save failed</span>
    </q-card-actions>

    <q-card-actions align="right">
      <q-btn label="Delete"
             color="negative"
             @click="showConfirmDelete = true"
             :loading="userDataSaveWaiting"
             class="text-negative q-mr-xl" />
      <q-btn label="Cancel" color="grey-6" v-close-popup />
      <q-btn label="Save"
             color="positive"
             @click="saveUser"
             :loading="userDataSaveWaiting"/>
    </q-card-actions>

    <q-inner-loading :showing="isLoading">
      <q-spinner-dots size="md" color="primary" />
    </q-inner-loading>
  </q-card>

  <q-dialog v-model="showConfirmDelete">
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="fas fa-trash" color="alert" text-color="primary" />
        <span class="q-ml-sm">Are you sure you want to delete this {{ dataType }}?</span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="grey-7" v-close-popup />
        <q-btn flat
               :loading="isDeleting"
               label="Delete"
               color="negative"
               @click="deleteEntry" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</q-dialog>
</template>

<script>
import LogViewer from 'components/LogViewer.vue'
import ActionViewer from 'components/ActionViewer.vue'

export default {
  name: 'UserEdit',

  props: {
    uuid: {
      type: String,
      required: true,
    },
    value: {
      type: Boolean,
      required: true,
    },
  },

  watch: {
    uuid () {
      this.loadData();
    },
    storedUser () {
      this.userData = JSON.parse(JSON.stringify(this.storedUser));
      if (Object.keys(this.userData).length)
        this.loadPermissions();
    }
  },

  components: {
    'log-viewer': LogViewer,
    'action-viewer': ActionViewer,
  },

  computed: {
    storedUser: {
      get () {
        return this.$store.state.entries.entry;
      },
    },
    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },

  data () {
    return {
      isLoading: false,
      isDeleting: false,
      loadingError: false,
      deleteError: false,
      showConfirmDelete: false,
      userData: {},
      dataType: 'user',
      isLoadingPermissions: false,
      loadPermissionsError: false,
      permissions: {},
      newApiKey: '',
      newApiKeyWaiting: false,
      newApiKeyError: false,
      userDataSaveError: false,
      userDataSaveWaiting: false,
      showActions: false,
      showLogs: false,
    }
  },

  methods: {
    loadData () {
      this.isLoading = true;
      this.loadingError = false;
      if (this.uuid === '' && this.uuid === 'default') {
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEmptyEntry', this.dataType)
              .catch(() => this.loadingError = true)
              .finally(() => this.isLoading = false);
          });
      }
      else {
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEntry', {'id': this.uuid,
                                                      'dataType': this.dataType})
              .catch(() => this.loadingError = true)
              .finally(() => this.isLoading = false);
          });
      }
    },
    
    loadPermissions () {
      this.isLoadingPermissions = true;
      this.loadPermissionsError = false;
      this.$store.dispatch('adminUsers/getPermissionTypes')
        .then((data) => {
          let key;
          for (key of data) {
            this.$set(this.permissions, key,
                      this.userData.permissions.includes(key));
          }
        })
        .catch((err) => this.loadPermissionsError = true)
        .finally(() => this.isLoadingPermissions = false);
    },

    updateVisibility (value) {
      this.$emit('input', value)
    },

    deleteEntry() {
      this.isDeleting = true;
      this.$store.dispatch('entries/deleteEntry', {'id': this.uuid,
                                                   'dataType': this.dataType})
        .then(() => {
          this.showConfirmDelete = false;
          this.updateVisibility(false);
          this.$emit('user-changed', true);
        })
        .catch((err) => this.deleteError = true)
        .finally(() => this.isDeleting = false);
    },

    saveUser () {
      this.userDataSaveError = false;
      this.userDataSaveWaiting = true;
      let toSubmit = JSON.parse(JSON.stringify(this.userData));
      if (this.uuid == '') {
        toSubmit.id = '';
      }
      else {
        toSubmit.id = toSubmit._id;
      }
      delete toSubmit._id;
      delete toSubmit.authIds;
      if (this.uuid === '') {
        delete toSubmit.apiKey;
        delete toSubmit.apiSalt;
      }
      if (!this.currentUser.permissions.includes('USER_MANAGEMENT'))
        delete toSubmit.permissions;
      else 
        toSubmit.permissions = Object.keys(this.permissions).filter((key) => this.permissions[key]);
      this.$store.dispatch('entries/saveEntry', {data: toSubmit,
                                                 dataType: this.dataType})
        .then(() => {
          this.updateVisibility(false);
          this.$emit('user-changed', true);
        })
        .catch(() => this.userDataSaveError = true)
        .finally(() => {
          this.userDataSaveWaiting = false;
          if (!this.userDataSaveError)
            this.loadData();
        });
    },

    generateNewApiKey () {
      this.newApiKeyWaiting = true;
      this.newApiKeyError = false;
      this.$store.dispatch('adminUsers/genApiKey', this.uuid)
        .then((response) => this.newApiKey = response.data.key)
        .catch(() => this.newApiKeyError = true)
        .finally(() => this.newApiKeyWaiting = false);
    },
  },

  mounted () {
    this.loadData();
  },
}
</script>
