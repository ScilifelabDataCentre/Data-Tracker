<template>
<q-dialog :value="value"
          @input="updateVisibility">
  <q-card>
    <q-card-section>
      <q-input outlined
               label="Email"
               v-model="userData.email" />
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
      <span class="text-h6">Permissions</span>
    </q-card-section>
    <q-card-section class="flex text-bold">
      <q-chip color="blue-9"
              text-color="white"
              v-for="perm in userData.permissions"
              :key="perm"
              :label="perm" />
    </q-card-section>
    <q-card-section>
      <span class="text-h6">API Key</span>
    </q-card-section>
    
    <q-card-section>
      <span class="text-h6">Authentication IDs:</span>
      <q-list>
        <q-item v-for="authId in userData.authIds"
                :key="authId">
          <q-item-section>
            {{ authId }}
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
    <q-card-section>
      <q-btn color="positive"
             label="Generate new API key"
             @click="generateNewApiKey" />
      <q-input outlined
               stack-label
               v-show="newApiKey.length > 0"
               label="New API Key"
               class="q-my-sm"
               :value="newApiKey"
               disable />
    </q-card-section>

    <q-card-actions align="right">
      <q-btn label="Cancel" color="grey-6" v-close-popup />
      <q-btn label="Save" color="positive" v-close-popup @click="saveUser"/>
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
      if (this.uuid === '') {
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEmptyEntry', 'user')
              .then(() => this.isLoading = false)
              .catch(() => this.isLoading = false);
          });
      }
      else {
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEntry', {'id': this.uuid,
                                                      'dataType': 'user'})
              .then(() => this.isLoading = false)
              .catch(() => this.isLoading = false);
          });
      }
    },
    storedUser () {
      this.userData = JSON.parse(JSON.stringify(this.storedUser));
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
      userData: {},
      newApiKey: '',
    }
  },

  methods: {
    updateVisibility (value) {
      this.$emit('input', value)
    },

    saveUser () {
    },

    generateNewApiKey () {
    },
  },

  mounted () {
  },
}
</script>
