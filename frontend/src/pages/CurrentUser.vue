<template>
<q-page padding>
  <h2>User Settings</h2>

  <q-card class="q-my-md">
    <q-card-section>
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
      <q-btn color="positive"
             class="q-mt-md"
             label="Save settings"
             @click="saveSettings" />
    </q-card-section>
  </q-card>

  <q-card>
    <q-card-section>
      <span class="text-h4">Permissions</span>
    </q-card-section>
    <q-card-section class="flex text-bold">
      <q-chip color="blue-9"
              text-color="white"
              v-for="perm in currentUser.permissions"
              :key="perm"
              :label="perm" />
    </q-card-section>
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <span class="text-h4">API Key</span>
    </q-card-section>
    
    <q-card-section>
      <span class="text-h6">Available Authentication IDs:</span>
      <q-list>
        <q-item v-for="authId in currentUser.authIds"
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
  </q-card>
</q-page>
</template>

<script>
import { format } from 'quasar'
const { capitalize } = format

export default {
  name: 'CurrentUserInfo',

  computed: {
    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
      set (newValue) {
        console.log(newValue)
        this.$store.dispatch('currentUser/updateInfo', newValue)
          .then(() => this.$store.dispatch('currentUser/getInfo'));
      }
    }
  },

  data () {
    return {
      userData: {},
      filter: '',
      pageAbout: '',
      pageNew: '',
      loading: true,
      newApiKey: '',
      newApiKeyError: false,
    }
  },

  methods: {
    saveSettings () {
      let toSubmit = JSON.parse(JSON.stringify(this.userData));
      this.currentUser = toSubmit;
    },

    generateNewApiKey () {
      this.$store.dispatch('currentUser/genApiKey')
        .then((response) => {
          this.newApiKey = response.data.key;
          console.log(response);
        })
        .catch(() => this.newApiKeyError = true);
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
