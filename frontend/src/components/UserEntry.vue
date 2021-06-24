<template>
<q-expansion-item expand-separator
                  icon="far fa-user"
                  :label="name">
  <q-list dense>
    <q-item v-if="contact.length === 0 
                  && affiliation.length === 0 
                  && url.length === 0
                  && orcid.length === 0">
      <q-item-section>
        <span class="text-grey">No extra information available</span>
      </q-item-section>
    </q-item>
    <q-item v-show="contact.length > 0">
      <q-item-section avatar>
        <q-avatar>
          <q-icon name="far fa-address-card"/>
        </q-avatar>
      </q-item-section>
      <q-item-section>
        {{ contact }}
      </q-item-section>
    </q-item>
    <q-item v-show="affiliation.length > 0">
      <q-item-section avatar>
        <q-avatar>
          <q-icon name="fas fa-university" />
        </q-avatar>
      </q-item-section>
      <q-item-section>
        {{ affiliation }}
      </q-item-section>
    </q-item>
    <q-item v-show="url.length > 0">
      <q-item-section avatar>
        <q-avatar>
          <q-icon name="fas fa-link" />
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <a class="std-link" :href="url">{{ url }}</a>
      </q-item-section>
    </q-item>
    <q-item v-show="orcid.length > 0">
      <q-item-section avatar>
        <q-avatar>
          <q-icon name="fab fa-orcid" />
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <a class="std-link" :href="'https://orcid.org/' + orcid">{{ orcid }}</a>
      </q-item-section>
    </q-item>
  </q-list>
</q-expansion-item>
</template>

<script>
export default {
  name: 'UserEntry',

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
