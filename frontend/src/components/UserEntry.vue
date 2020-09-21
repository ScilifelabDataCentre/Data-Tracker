<template>
<q-item class=".col-12"
        clickable
        @click="isOpen = !isOpen" >
  <q-item-section>
    {{ name }}
    <q-slide-transition>
      <div v-show="isOpen">
        <q-list dense>
          <q-item v-show="contact.length > 0">
            <q-item-section avatar>
              <q-avatar>
                <q-icon name="contact_mail" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              {{ contact }}
            </q-item-section>
          </q-item>
          <q-item v-show="affiliation.length > 0">
            <q-item-section avatar>
              <q-avatar>
                <q-icon name="business" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              {{ affiliation }}
            </q-item-section>
          </q-item>
          <q-item v-show="url.length > 0">
            <q-item-section avatar>
              <q-avatar>
                <q-icon name="link" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              {{ url }}
            </q-item-section>
          </q-item>
          <q-item v-show="orcid.length > 0">
            <q-item-section avatar>
              <q-avatar>
                <q-icon name="account_circle" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              {{ orcid }}
            </q-item-section>
          </q-item>
        </q-list>
      </div>
    </q-slide-transition>
  </q-item-section>
  <q-item-section avatar>
    <q-icon :name="isOpen ? 'arrow_drop_up' : 'arrow_drop_down'" />
  </q-item-section>
</q-item>
</template>

<script>
export default {
  name: 'UserInfo',

  props: {
    name: {
      type: String,
      required: true,
    },
    contact: {
      type: String,
      required: true,
    },
    url: {
      type: String,
      required: true,
    },
    orcid: {
      type: String,
      required: true,
    },
    affiliation: {
      type: String,
      required: true,
    },
  },
  
  data () {
    return {
      isOpen: false,
    }
  }
  
}
</script>
