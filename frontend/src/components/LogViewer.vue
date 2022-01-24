<template>
<q-dialog :model-value="modelValue"
          @update:model-value="updateVisibility">
  <q-card id="log-viewer-dialog">
    <q-card-section class="text-h5 text-center">
      Entry History
    </q-card-section>
    <q-card-section>
      <q-list>
        <q-expansion-item expand-separator
                          v-for="entry in logs"
                          :key="entry._id"
                          :label="capitalize(entry.comment) + ' (' + entry.action.toUpperCase() + ')'"
                          :caption="entry.timestamp">
          <q-card>
            <q-list>
              <q-item>
                <q-item-section>
                  <q-field stack-label
                           outlined
                           label="User">
                    {{ entry.user }}
                  </q-field>
                </q-item-section>
              </q-item>
              <q-item-label caption>
                Changes
              </q-item-label>
              <q-item v-for="key in Object.keys(entry.data)" :key="key">
                <q-item-section>
                  <q-field stack-label
                           outlined
                           :label="key">
                    {{ entry.data[key] }}
                  </q-field>
                  </q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </q-expansion-item>
      </q-list>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat label="Done" color="primary" v-close-popup />
    </q-card-actions>

    <q-inner-loading :showing="isLoading">
      <q-spinner-dots size="50px" color="primary" />
    </q-inner-loading>
  </q-card>
</q-dialog>
</template>

<script>
import { format } from 'quasar'
const { capitalize } = format

export default {
  name: 'LogViewer',

  props: {
    dataType: {
      type: String,
      required: true
    },
    uuid: {
      type: String,
      default: '',
    },
    modelValue: {
      type: Boolean,
      required: true,
    },
  },

  emits: ['update:modelValue'],

  computed: {
    logs: {
      get () {
        return this.$store.state.entries.logs;
      },
    },
  },

  watch: {
    value: function(val) {
      if (val)
        if (val && (this.uuid !== '')) {
          this.$store.dispatch('entries/resetEntryLog')
            .then(() => {
              this.$store.dispatch('entries/getEntryLog', {'id': this.uuid,
                                                           'dataType': this.dataType})
                .finally(() => this.isLoading = false);
            });
        }
    }
  },

  data () {
    return {
      isLoading: true,
    }
  },

  methods: {
    updateVisibility(value) {
      this.$emit('update:modelValue', value)
    },

    'capitalize': capitalize,
  },
}
</script>
