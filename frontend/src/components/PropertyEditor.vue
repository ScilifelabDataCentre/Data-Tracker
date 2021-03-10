<template>
<div>
  <div class="row q-my-md">
    <q-input stack-label
             outlined
             label="New Property Name"
             v-model="key"
             @keyup.enter="addProperty"
             class="col-10" />
    <q-btn icon="fas fa-tags"
           color="positive"
           @click="addProperty"
           label="Add"
           class="col-2"
           flat/>
  </div>
  <q-list dense>
    <q-item v-for="propertyKey of Object.keys(fieldEntries)" :key="propertyKey">
      <q-item-section>
        <q-input stack-label
                 outlined
                 :label="propertyKey"
                 @input="setProperty(propertyKey, $event)"
                 :value="fieldEntries[propertyKey]">
          <template v-slot:append>
            <q-icon name="fas fa-minus-circle"
                    color="negative"
                    @click="deleteProperty(propertyKey)"
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
  <q-inner-loading :showing="isLoading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</div>
</template>

<script>
export default {
  name: 'PropertyEditor',

  computed: {
    fieldEntries: {
      get () {
        if (!this.isLoading)
          return this.$store.state.entries.entry[this.fieldDataName];
        return {}
      }
    },
  },

  props: {
    fieldDataName: {
      type: String,
      required: true,
    },
    isLoading: {
      type: Boolean,
      default: true
    }
  },

  data () {
    return {
      key: '',
    }
  },

  methods: {
    addProperty(event) {
      event.preventDefault();
      if (this.key.length > 0 && !Object.keys(this.fieldEntries).includes(this.key)) {
        this.$store.dispatch('entries/addProperty',
                             {'propertyName': this.fieldDataName,
                              'key': this.key});
        this.key = '';
      }
    },

    setProperty(keyName, value) {
      let outObject = {};
      outObject[keyName] = value;
      this.$store.dispatch('entries/setProperty',
                           {'propertyName': this.fieldDataName,
                            'value': outObject});
    },

    deleteProperty(keyName) {
      this.$store.dispatch('entries/deleteProperty',
                           {'propertyName': this.fieldDataName, 'key': keyName});
    },
  },
}
</script>
