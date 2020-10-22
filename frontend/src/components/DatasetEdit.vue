<template>
<div>
  <q-card class="q-my-sm">
    <q-card-section>
      <q-field v-if="dataset._id !== ''"
               label="UUID"
	       stack-label
	       filled>
        <template v-slot:prepend>
          <q-icon name="label_important" />
        </template>
        <template v-slot:control>
          {{ dataset._id }}
        </template>
      </q-field>
    </q-card-section>
  
    <q-card-section>
      <q-input id="dataset-title"
               label="Title"
               v-model="title"
               outlined>
        <template v-slot:prepend>
          <q-icon name="title" />
        </template>
      </q-input>
    </q-card-section>
    <q-card-section>
      <q-input id="dataset-description"
               type="textarea"
               label="Description"
               v-model="description"
               autogrow
               outlined
               bottom-slots>
        <template v-slot:prepend>
          <q-icon name="description" />
        </template>
        <template v-slot:hint>
          Use <a class="std-link"
                 href="https://www.markdownguide.org/cheat-sheet/"
                 target="_blank">Markdown</a> to format the description.
        </template>
      </q-input>
    </q-card-section>
  </q-card>

  <q-card>
    <q-card-section>
      <tag-editor fieldTitle="Standard Tags"
                  helpText="Set standard tags"
                  fieldDataName="tagsStandard"
                  :isLoading="isLoading"/>
    </q-card-section>
    <q-card-section>
      <tag-editor fieldTitle="User Tags"
                  helpText="Set user tags"
                  fieldDataName="tagsUser"
                  :isLoading="isLoading"/>
    </q-card-section>
  </q-card>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'DatasetEdit',

  components: {
    'tag-editor': TagEditor,
  },

  props: {    
    isLoading: {
      type: Boolean,
      default: true
    }
  },

  computed: {
    dataset: {
      get () {
        return this.$store.state.entries.entry;
      },
    },

    title: {
      get () {
        return this.$store.state.entries.entry.title;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'title': newValue});
      },
    },

    description: {
      get () {
        return this.$store.state.entries.entry.description;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'description': newValue});
      },
    },

    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },

  data () {
    return {
      addDsError: '',
      deleteDsError: '',
      linkDesc: '',
      tagName: '',
      isSending: false,
      userList: [],
    }
  },

  methods: {
    setField(event, data) {
      event.preventDefault();
      this.$store.dispatch('entries/setEntryFields', data);
    },
  },

  mounted () {
    this.$store.dispatch('adminUsers/getUsers');    
  }
}
</script>
