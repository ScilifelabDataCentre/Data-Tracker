<template>
<div>
  <div class="q-my-md"
       id="property-editor-new-key">
    <q-input stack-label
             outlined
             label="New Property Name"
             v-model="key"
             @keyup.enter="addProperty"
             :rules="[ function (val) { return (enableAdd || val.length === 0) || 'Must contain at least 3 characters, no whitespace at beginning nor end, and must not already exist.' }]">
      <template v-slot:after>
        <q-btn icon="fas fa-plus"
               dense
               rounded
               size="md"
               :disabled="!enableAdd"
               color="positive"
               @click="addProperty" />
        </template>
    </q-input>
  </div>
  <q-list dense
          id="property-editor-key-list">
    <q-item v-for="propertyKey of Object.keys(propertyEntries)" :key="propertyKey">
      <q-item-section>
        <q-input stack-label
                 outlined
                 :label="propertyKey"
                 :rules="[ function (val) { return evaluateField(val) || 'At least three characters, no whitespace at beginning nor end.' }]"
                 @update:model-value="setProperty(propertyKey, $event)"
                 :model-value="propertyEntries[propertyKey]">
          <template v-slot:prepend>
            <q-icon name="fas fa-tag"
                    color="primary"/>
          </template>
        </q-input>
      </q-item-section>
    </q-item>
  </q-list>
  <div class="flex">
    <q-chip square
            removable
            color="grey-3"
            v-for="propertyKey of Object.keys(propertyEntries)"
            :key="propertyKey"
            :rules="[ function (val) { return (evaluateField(val) || val.length === 0) || 'At least three characters, no whitespace at beginning nor end.' }]"
            @remove="deleteProperty(propertyKey)">
      <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ propertyKey }}</span> {{ propertyEntries[propertyKey] }}
    </q-chip>
  </div>

  <q-inner-loading :showing="isLoading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</div>
</template>

<script>
export default {
  name: 'PropertyEditor',

  computed: {
    enableAdd: {
      get () {
        return this.evaluateKey(this.key);
      },
    },

    propertyEntries: {
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
    evaluateField (val) {
      return val.length >= 3 && val.trim() === val;
    },

    evaluateKey (val) {
      return this.evaluateField(val) && !Object.keys(this.propertyEntries).includes(val);
    },
    
    addProperty(event) {
      event.preventDefault();
      if (this.enableAdd) {
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
