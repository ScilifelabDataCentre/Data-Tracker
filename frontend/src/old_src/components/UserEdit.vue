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
        <q-item v-if="uuid !== ''">
          <q-item-section>
            <q-input outlined
                     filled
                     stack-label
                     label="UUID"
                     v-model="userData.id"
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
          <q-item class="column">
            <q-checkbox v-for="field of Object.keys(permissions)"
                        :key="field"
                        dense
                        v-model="permissions[field]"
                        :label="field" />
          </q-item>
          <q-inner-loading :showing="isLoadingPermissions">
            <q-spinner-dots size="md" color="primary" />
          </q-inner-loading>
        </div>
        <div v-if="uuid !== ''">
          <q-item-label caption>Authentication IDs</q-item-label>
          <q-item class="column">
            <div v-for="authId in userData.auth_ids"
                 :key="authId">
              {{ authId }}
            </div>
          </q-item>
          <q-item-label caption>API Key</q-item-label>
          <q-item id="user-edit-api-key">
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
      </q-list>
    </q-card-section>

    <q-card-actions v-if="currentUser.permissions.includes('USER_MANAGEMENT') && uuid !==''"
                    align="left">
      <q-btn label="Logs"
             color="primary"
             class="q-mx-sm user-edit-logs"
             @click="showLogs = true"/>
      <q-btn label="Actions"
             color="primary"
             class="q-mx-sm user-edit-actions"
             @click="showActions = true"/>
      <log-viewer v-model="showLogs"
                  dataType="user"
                  :uuid="uuid"/>
      <action-viewer v-model="showActions"
                     :uuid="uuid" />
    </q-card-actions>

    <q-card-actions align="right">
      <span v-show="userDataSaveError" class="text-negative">Save failed</span>
    </q-card-actions>
    <q-card-actions align="right">
      <q-btn v-if="uuid !== ''"
             label="Delete"
             color="negative"
             @click="showConfirmDelete = true"
             :loading="userDataSaveWaiting"
             class="text-negative q-mr-xl user-edit-delete" />

      <q-btn label="Save"
             color="positive"
             class="user-edit-save"
             type="submit"
             @click="saveUser"
             :loading="userDataSaveWaiting"/>
      <q-btn class="user-edit-cancel"
             label="Cancel"
             color="grey-6"
             v-close-popup />
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
        <q-btn flat
               :loading="isDeleting"
               label="Delete"
               color="negative"
               class="user-edit-confirm-delete"
               @click="deleteEntry" />
        <q-btn flat label="Cancel" color="grey-7" v-close-popup />
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
      // visibility for v-model
      type: Boolean,
      required: true,
    },
  },

  watch: {
    uuid () {
      this.loadData();
    },
  },

  components: {
    'log-viewer': LogViewer,
    'action-viewer': ActionViewer,
  },

  computed: {
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
      if (this.uuid === '' || this.uuid === 'default') {
        this.userData = {};
        this.$store.dispatch('entries/getLocalEmptyEntry', this.dataType)
          .then((data) => this.userData = data)
          .catch(() => this.loadingError = true)
          .finally(() => this.isLoading = false);
        for (const key in this.permissions)
          this.permissions[key] = false;
      }
      else {
        this.$store.dispatch('entries/getLocalEntry', {'id': this.uuid,
                                                       'dataType': this.dataType})
          .then((data) => {
            this.userData = data;
            for (const key in this.permissions)
              this.permissions[key] = this.userData.permissions.includes(key)
          })
          .catch(() => this.loadingError = true)
          .finally(() => this.isLoading = false);
      }
    },
    
    loadPermissions () {
      this.isLoadingPermissions = true;
      this.loadPermissionsError = false;
      this.$store.dispatch('adminUsers/getPermissionTypes')
        .then((data) => {
          if (this.uuid !== '' && this.uuid !== 'default') {
            let key;
            for (key of data) {
              this.$set(this.permissions, key,
                        this.userData.permissions.includes(key));
            }
          }
          else {
            let key;
            for (key of data) {
              this.$set(this.permissions, key,
                        false);
            }
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
      let toSubmit = {};
      toSubmit.name = this.userData.name;
      toSubmit.affiliation = this.userData.affiliation;
      toSubmit.email = this.userData.email;
      toSubmit.contact = this.userData.contact;
      toSubmit.orcid = this.userData.orcid;
      toSubmit.url = this.userData.url;

      if (this.currentUser.permissions.includes('USER_MANAGEMENT'))
        toSubmit.permissions = Object.keys(this.permissions).filter((key) => this.permissions[key]);

      this.$store.dispatch('entries/saveEntry', {id: this.uuid,
                                                 data: toSubmit,
                                                 dataType: this.dataType})
        .then(() => {
          this.updateVisibility(false);
          this.$emit('user-changed', true);
          this.loadData();
        })
        .catch(() => this.userDataSaveError = true)
        .finally(() => this.userDataSaveWaiting = false);
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
    if (this.currentUser.permissions.includes('USER_MANAGEMENT')) {
      this.loadPermissions()
    }
  },
}
</script>
