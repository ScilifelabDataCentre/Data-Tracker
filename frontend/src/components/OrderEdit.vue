<template>
<div>
  <q-field v-if="order._id !== ''"
           label="UUID"
           class="q-mb-lg"
	   stack-label
	   filled>
    <template v-slot:prepend>
      <q-icon name="label_important" />
    </template>
    <template v-slot:control>
      {{ order._id }}
    </template>
  </q-field>

  <q-input id="order-title"
           class="q-my-md"
           label="Title"
           v-model="title"
           :rules="[ val => val.length > 0 ]"
           outlined>
    <template v-slot:prepend>
      <q-icon name="title" />
    </template>
  </q-input>

  <div class="q-my-md">
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
  </div>

  <q-list bordered
          class="q-my-lg">
    <q-expansion-item expand-separator
                      icon="fas fa-tags"
                      label="Tags"
                      caption="Set labels (tags)">
      <q-card>
        <q-card-section>
          <tag-editor :isLoading="isLoading"
                      v-model="tags"/>
        </q-card-section>
      </q-card>
    </q-expansion-item>

    <q-expansion-item expand-separator
                      icon="fas fa-tags"
                      label="Properties"
                      caption="Set properties (key: value)">
      <q-card>
        <q-card-section>
          <property-editor fieldTitle="Properties"
                           helpText="Set properties"
                           fieldDataName="properties"
                           :isLoading="isLoading"/>
        </q-card-section>
      </q-card>
    </q-expansion-item>

    <q-separator />

    <q-expansion-item expand-separator
                      icon="far fa-user"
                      label="Authors"
                      caption="The ones who own the sample (e.g. PI)">
      <user-selector fieldTitle="Authors"
                     fieldDataName="authors"
                     class="q-my-sm"
                     helpText="The ones who own the sample (e.g. PI)"
                     :isLoadingUsers="isLoadingUsers"
                     :isLoading="isLoading"/>
    </q-expansion-item>

    <q-expansion-item expand-separator
                      icon="far fa-user"
                      label="Generators"
                      caption="The ones who generated the data (e.g. Facility)">
      <user-selector fieldTitle="Generators"
                     fieldDataName="generators"
                     class="q-my-sm"
                     helpText="The ones who generated the data (e.g. Facility)"
                     :isLoadingUsers="isLoadingUsers"
                     :isLoading="isLoading"/>
    </q-expansion-item>

    <q-expansion-item expand-separator
                      icon="far fa-user"
                      label="Organisation"
                      caption="The data controller (e.g. university)">
      <user-selector fieldTitle="Organisation"
                     fieldDataName="organisation"
                     selectType="single"
                     class="q-my-sm"
                     helpText="The data controller (e.g. university)"
                     :isLoadingUsers="isLoadingUsers"
                     :isLoading="isLoading"/>
    </q-expansion-item>

    <q-expansion-item expand-separator
                      icon="far fa-user"
                      label="Editors"
                      caption="Users who may edit this order and the associated datasets">
      <user-selector fieldTitle="Editors"
                     fieldDataName="editors"
                     class="q-my-sm"
                     helpText="Users who may edit this order and the associated datasets"
                     value="order.editors"
                     :isLoadingUsers="isLoadingUsers"
                     :isLoading="isLoading"/>
    </q-expansion-item>
  </q-list>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'
import PropertyEditor from 'components/PropertyEditor.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'OrderEdit',

  components: {
    'user-selector': UserSelector,
    'property-editor': PropertyEditor,
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

    tags: {
      get () {
        return this.$store.state.entries.entry.tags;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'tags': newValue});
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
    this.$store.dispatch('entries/getEntries', 'user')
      .then(() => this.isLoadingUsers = false)
      .catch(() => this.isLoadingUsers = false);
  }
}
</script>
