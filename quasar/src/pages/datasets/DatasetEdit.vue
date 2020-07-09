<template>
<q-page padding>
  <q-card>
    <q-form ref="dataset-edit">
      <q-card-section>
        <q-field
	  v-if="newDataset.id !== '-1'"
          label="UUID"
	  stack-label
	  filled
          >
	  <template v-slot:prepend>
            <q-icon name="label_important" />
          </template>
	  <template v-slot:control>
            {{ newDataset.id }}
          </template>
	</q-field>
      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">General</div>
        <q-input id="dataset-title"
                 label="Title"
                 v-model="newDataset.title">
	  <template v-slot:prepend>
            <q-icon name="title" />
          </template>
	</q-input>
        <q-input id="dataset-description"
                 type="textarea"
                 label="Description"
                 v-model="newDataset.description"
                 autogrow>
	  <template v-slot:prepend>
            <q-icon name="description" />
          </template>
	</q-input>
      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">Links</div>
        <div class="row flex">
          <q-input class="col-5 q-mr-md"
                   id="dataset-description"
                   label="Description"
                   v-model="linkDesc" />
           <q-btn flat icon="add" color="blue" @click="addLink"/>
         </div>
        <q-list dense>
          <q-item v-for="(link, i) in newDataset.links" :key="i">
            <q-input :label="link.description"
                     v-model="link.url"
                     stack-label>
              <template v-slot:prepend>
                <q-icon name="link" />
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteLink($event, i)" />
              </template>
            </q-input>
          </q-item>
        </q-list>
      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">User Tags</div>
        <div class="row flex">
          <q-input class="col-5 q-mr-md"
                   id="dataset-description"
                   label="User tag name"
                   v-model="tagName" />
           <q-btn flat icon="add" color="blue" @click="addUserTag"/>
         </div>
        <q-list dense>
          <q-item v-for="key in Object.keys(newDataset.extra)" :key="key">
            <q-input :label="key"
                     v-model="newDataset.extra[key]"
                     stack-label>
              <template v-slot:prepend>
                <q-icon name="label" />
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteUserTag($event, i)" />
              </template>
            </q-input>
          </q-item>
        </q-list>
      </q-card-section>

    </q-form>
  </q-card>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
export default {
  name: 'DatasetEdit',

  props: {
    uuid: {
      type: String,
      required: true
    }
  },

  computed: {
    origDataset: {
      get () {
        return this.$store.state.datasets.dataset;
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
      loading: true,
      newDataset: {
        id: '-1',
        title: '',
        description: '',
        links: [],
        linkDesc: '',
        extra: {},
      },
      linkDesc: '',
      tagName: '',
    }
  },

  methods: {    
    addLink(event) {
      event.preventDefault();
      this.newDataset.links.push({'description': this.linkDesc,
                                  'url': ''});
      this.linkDesc = '';
    },

    deleteLink(event, position) {
      event.preventDefault();
      this.newDataset.links.splice(position, 1);
    },

    addUserTag(event) {
      event.preventDefault();
      if (this.tagName !== '') {
        if (! Object.keys(this.newDataset.extra).includes(this.tagName)) {
          this.$set(this.newDataset.extra, this.tagName, '');
        }
      }
      this.tagName = '';
    },

    deleteUserTag(event, keyName) {
      event.preventDefault();
      this.$delete(this.newDataset.extra, keyName);
    },

  },
  
  mounted () {
    this.$store.dispatch('datasets/getDataset', this.uuid)
      .then((response) => {
        this.newDataset = JSON.parse(JSON.stringify(response.data.dataset));
        this.newDataset.id = this.newDataset._id;
        delete this.newDataset._id;
        delete this.newDataset.related;
        delete this.newDataset.projects;
        this.loading = false;
      })
      .catch(() => this.loading = false);
  }

}
</script>
