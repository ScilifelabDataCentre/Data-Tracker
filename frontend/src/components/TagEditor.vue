<template>
<div>
  <span class="text-h6">{{ fieldTitle }}</span>
  <div class="row q-my-md">
    <q-input stack-label
             outlined
             label="New Tag Name"
             v-model="key"
             @keyup.enter="addTag"
             class="col-10" />
    <q-btn icon="fas fa-tag"
           color="positive"
           @click="addTag"
           label="Add"
           class="col-2"
           flat/>
  </div>
  <q-list dense>
    <q-item v-for="tagKey of Object.keys(fieldEntries)" :key="tagKey">
      <q-item-section>
        <q-input stack-label
                 outlined
                 :label="tagKey"
                 @input="setTag(tagKey, $event)"
                 :value="fieldEntries[tagKey]">
          <template v-slot:append>
            <q-icon name="fas fa-minus-circle"
                    color="negative"
                    @click="deleteTag(tagKey)"
                    class="cursor-pointer" />
          </template>
          <template v-slot:prepend>
            <q-icon name="fas fa-tag"
                    color="primary"/>
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

    isLoading: {
      type: Boolean,
      default: false
    }
  },

  data () {
    return {
      key: '',
    }
  },

  methods: {
    addTag(event) {
      event.preventDefault();
      if (this.key.length > 0 && !Object.keys(this.fieldEntries).includes(this.key)) {
        this.$store.dispatch('entries/addTag',
                             {'tagName': this.fieldDataName,
                              'key': this.key});
        this.key = '';
      }
    },

    setTag(keyName, value) {
      let outObject = {};
      outObject[keyName] = value;
      this.$store.dispatch('entries/setTag',
                           {'tagName': this.fieldDataName,
                            'value': outObject});
    },

    deleteTag(keyName) {
      this.$store.dispatch('entries/deleteTag',
                           {'tagName': this.fieldDataName, 'key': keyName});
    },
  },
}
</script>
