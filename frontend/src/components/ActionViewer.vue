<template>
<q-dialog :value="value"
          @input="updateVisibility">
  <q-card>
    <q-card-section class="text-h5 text-center">
      User Actions
    </q-card-section>
    <q-card-section>
      <div v-if="!isLoading && actions.length === 0">
        No actions logged for user.
      </div>
      <q-list>
        <q-expansion-item expand-separator
                          v-for="entry in actions"
                          :key="entry._id"
                          :label="capitalize(entry.comment) + ' (' + entry.action.toUpperCase() + ')'"
                          :caption="entry.timestamp">
          <q-card>
            <q-list dense>
              <q-item>
                <q-item-section>
                  <q-field stack-label
                           label="Data Type"
                           outlined>
                    {{ capitalize(entry.dataType) }}
                  </q-field>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-field stack-label
                           label="Entry UUID"
                           outlined>
                    {{ entry.entryId }}
                  </q-field>
                </q-item-section>
              </q-item>
              <q-item v-if="entry.dataType !== 'user'">
                <q-item-section>
                  <q-btn flat
                         color="primary"
                         :label="'Go to ' + entry.dataType"
                         :to="{ 'name': capitalize(entry.dataType) + ' About', 'params': { 'uuid': entry.entryId } }" />
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
  name: 'ActionViewer',

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

  computed: {
    actions: {
      get () {
        return this.$store.state.entries.actions;
      },
    },
  },

  data () {
    return {
      isLoading: true,
    }
  },

  methods: {
    updateVisibility(value) {
      this.$emit('input', value)
    },

    'capitalize': capitalize,
  },

  mounted () {
    if (this.uuid !== '') {
      this.$store.dispatch('entries/resetUserActions')
        .then(() => {
          this.$store.dispatch('entries/getUserActions', this.uuid)
            .finally(() => this.isLoading = false);
        });
    }
  },
}
</script>
