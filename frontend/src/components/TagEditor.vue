<template>
<div>
  <span class="text-h6">{{ fieldTitle }}</span>
  <q-list>
    <q-item>
      <q-item-section>
        <q-input stack-label
                 outlined
                 label="Tag Name"
                 v-model="key">
          <template v-slot:append>
            <q-icon name="fas fa-plus-circle"
                    color="positive"
                    @click="addTag"
                    class="cursor-pointer" />
          </template>
        </q-input>
      </q-item-section>
    </q-item>
    <q-item v-for="tagKey in Object.keys(fieldEntries)" :key="tagKey">
      <q-item-section>
        <q-input stack-label
                 outlined
                 :label="tagKey"
                 v-model="tags[tagKey]">
          <template v-slot:append>
            <q-icon name="fas fa-plus-circle"
                    color="positive"
                    @click="addTag"
                    class="cursor-pointer" />
          </template>
        </q-input>
      </q-item-section>
    </q-item>
  </q-list>
</div>
</template>

<script>
export default {
  name: 'TagEditor',

  computed: {
    fieldEntries: {
      get () {
        return this.$store.state.entries.entry[this.fieldDataName];
      }
    },
  },

  watch: {
    tags (newValue, OldValue) {
      let data = {};
      data[this.fieldDataName] = JSON.parse(JSON.stringify(newValue));
      this.$store.dispatch('entries/setEntryFields', data);
    },

    dataLoaded (newValue, OldValue) {
      this.tags = JSON.parse(JSON.stringify(this.fieldEntries[this.fieldDataName]));
    },
  },
  
  props: {
    fieldTitle: {
      type: String,
      required: true,
    },

    fieldDataName: {
      type: String,
      required: true,
    },

    helpText: {
      type: String,
      default: '',
    },

    dataLoaded: {
      type: Boolean,
      default: false
    }
  },

  
  data () {
    return {
      key: '',
      value: '',
      tags: {},
    }
  },

  methods: {
    addTag(event) {
      event.preventDefault();
      this.$set(this.tags, this.key, '');
    },

    deleteUserTag(event, keyName) {
      event.preventDefault();
      this.$delete(this.newEntry.extra, keyName);
    },

    setField(event, data) {
      event.preventDefault();
      if (this.fieldDataName === 'organisation')
        
        this.$store.dispatch('entries/setEntryFields', data);
    },
  },

  mounted () {
      this.tags = JSON.parse(JSON.stringify(this.fieldEntries[this.fieldDataName]));
  }
}
</script>
