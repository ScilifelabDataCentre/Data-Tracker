<template>
<div>
  <q-card class="q-my-sm">
    <q-card-section>
      <q-field v-if="order._id !== ''"
               label="UUID"
	       stack-label
	       filled>
        <template v-slot:prepend>
          <q-icon name="label_important" />
        </template>
        <template v-slot:control>
          {{ order._id }}
        </template>
      </q-field>
    </q-card-section>
  
    <q-card-section>
      <q-input id="order-title"
               label="Title"
               v-model="title"
               outlined>
        <template v-slot:prepend>
          <q-icon name="title" />
        </template>
      </q-input>
    </q-card-section>
    <q-card-section>
      <q-input id="order-description"
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

  <user-selector fieldTitle="Authors"
                 fieldDataName="authors"
                 class="q-my-sm"
                 helpText="The ones who own the sample (e.g. PI)"
                 :isLoadingUsers="isLoadingUsers"
                 :isLoading="isLoading"/>

  <user-selector fieldTitle="Generators"
                 fieldDataName="generators"
                 class="q-my-sm"
                 helpText="The ones who generated the data (e.g. Facility)"
                 :isLoadingUsers="isLoadingUsers"
                 :isLoading="isLoading"/>

  <user-selector fieldTitle="Organisation"
                 fieldDataName="organisation"
                 selectType="single"
                 class="q-my-sm"
                 helpText="The data controller (e.g. university)"
                 :isLoadingUsers="isLoadingUsers"
                 :isLoading="isLoading"/>

  <user-selector fieldTitle="Editors"
                 fieldDataName="editors"
                 class="q-my-sm"
                 helpText="Users who may edit this order and the associated datasets"
                 value="order.editors"
                 :isLoadingUsers="isLoadingUsers"
                 :isLoading="isLoading"/>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'OrderEdit',

  components: {
    'user-selector': UserSelector,
    'tag-editor': TagEditor,
  },

  props: {    
    isLoading: {
      type: Boolean,
      default: true
    }
  },

  computed: {
    order: {
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
      isLoadingUsers: false,
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
    this.isLoadingUsers = true;
    this.$store.dispatch('adminUsers/getUsers')
      .then(() => this.isLoadingUsers = false)
      .catch(() => this.isLoadingUsers = false);
  }
}
</script>
