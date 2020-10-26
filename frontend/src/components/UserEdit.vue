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
                  color="primary"
                  text-color="white"
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
      </q-list>    
    </q-card-section>

    <q-card-actions align="right">
      <q-btn label="Cancel" color="grey-6" v-close-popup />
      <q-btn label="Save" color="positive" @click="saveUser"/>
    </q-card-actions>

    <q-inner-loading :showing="isLoading">
      <q-spinner-dots size="md" color="primary" />
    </q-inner-loading>
  </q-card>
</q-dialog>
</template>

<script>
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
      this.isLoading = true;
      this.loadingError = false;
      if (this.uuid === '') {
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
    storedUser () {
      this.userData = JSON.parse(JSON.stringify(this.storedUser));
      if (Object.keys(this.userData).length)
        this.loadPermissions();
    }
  },

  computed: {
    storedUser: {
      get () {
        return this.$store.state.entries.entry;
      },
    },
  },

  data () {
    return {
      isLoading: false,
      loadingError: false,
      userData: {},
      dataType: 'user',
      isLoadingPermissions: false,
      loadPermissionsError: false,
      permissions: {},
      newApiKey: '',
      newApiKeyWaiting: false,
      newApiKeyError: false,
      userDataSaveError: false,
      userDataSaveWaiting: true,
    }
  },

  methods: {
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

    saveUser () {
      this.userDataSaveError = false;
      this.userDataSaveWaiting = true;
      let toSubmit = JSON.parse(JSON.stringify(this.userData));
      toSubmit.id = toSubmit._id;
      delete toSubmit._id;
      delete toSubmit.authIds;
      toSubmit.permissions = Object.keys(this.permissions).filter((key) => this.permissions[key]);
      console.log(toSubmit);
      this.$store.dispatch('entries/saveEntry', {data: toSubmit,
                                                 dataType: this.dataType})
        .then(() => this.updateVisibility(false))
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
}
</script>
