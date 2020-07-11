<template>
<q-page padding>
  <q-card>
    <q-card-section>
      <q-field
	v-if="newCollection.id !== ''"
        label="UUID"
	stack-label
	  filled
          >
	  <template v-slot:prepend>
            <q-icon name="label_important" />
          </template>
	  <template v-slot:control>
            {{ newCollection.id }}
          </template>
	</q-field>
      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">General</div>
        <q-input id="collection-title"
                 label="Title"
                 v-model="newCollection.title">
	  <template v-slot:prepend>
            <q-icon name="title" />
          </template>
	</q-input>
        <q-input id="collection-description"
                 type="textarea"
                 label="Description"
                 v-model="newCollection.description"
                 autogrow>
	  <template v-slot:prepend>
            <q-icon name="description" />
          </template>
	</q-input>
      </q-card-section>

      <q-card-section>
        <q-input id="collection-title"
                 label="Contact"
                 v-model="newCollection.contact">
	  <template v-slot:prepend>
            <q-icon name="contacts" />
          </template>
        </q-input>

        <div class="text-h6 q-mt-sm q-mb-xs">Datasets</div>
        <div class="row flex">
          <q-select outlined v-model="model"
                    :options="availableDatasets"
                    :dense="dense"
                    :options-dense="denseOpts"
                    @change="addDataset">
            <template v-slot:prepend>
              <q-icon name="insights" />
            </template>
          </q-select>
        </div>

        <q-list dense>
          <q-item v-for="(ds, i) in newCollection.datasets" :key="i">
            <q-field :label="ds._id"
                     stack-label>
              <template v-slot:prepend>
                <q-icon name="insights" />
              </template>
              <template v-slot:control>
                {{ ds.title }}
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteDataset($event, i)" />
              </template>
            </q-field>
          </q-item>
        </q-list>

        <div class="text-h6 q-mt-sm q-mb-xs">Publications</div>
        <q-btn round icon="add" color="positive" @click="addPublication"/>

        <q-list dense>
          <q-item v-for="(publication, i) in newCollection.publications" :key="i">
            <q-input label="Identifier"
                     stack-label
                     v-model="newCollection.publications[i]">
              <template v-slot:prepend>
                <q-icon name="article" />
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteDataset($event, ds._id)" />
              </template>
            </q-input>
          </q-item>
        </q-list>

      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">User Tags</div>
        <div class="row flex">
          <q-input class="col-5 q-mr-md"
                   id="add-tag"
                   label="User tag name"
                   v-model="tagName" />
           <q-btn flat icon="add" color="primary" @click="addUserTag"/>
         </div>
        <q-list dense>
          <q-item v-for="key in Object.keys(newCollection.extra)" :key="key">
            <q-input :label="key"
                     v-model="newCollection.extra[key]"
                     stack-label>
              <template v-slot:prepend>
                <q-icon name="label" />
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteUserTag($event, key)" />
              </template>
            </q-input>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-section>
        <q-btn label="Submit" color="positive" class="q-mr-md" @click="submitCollectionForm"/>
        <q-btn label="Cancel" color="blue-grey-4" class="q-mr-lg" @click="cancelChanges"/>
        <q-btn label="Delete" color="negative" class="q-ml-xl" @click="deleteCollection"/>
      </q-card-section>
  </q-card>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
export default {
  name: 'CollectionEdit',

  props: {
    uuid: {
      type: String,
      required: true
    }
  },

  computed: {
    origCollection: {
      get () {
        return this.$store.state.collections.collection;
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
      newCollection: {
        id: '',
        title: '',
        description: '',
        creator: '',
        receiver: '',
        extra: {},
      },
      availableDatasets: [],
      newDataset: '',
      newPublication: '',
      linkDesc: '',
      tagName: '',
    }
  },

  methods: {    
    addDataset(event, i) {
      event.preventDefault();
      this.newProject.publications.push(this.availableDatasets[i]);
      this.publication = '';
    },
      
    deleteDataset(event, uuid) {
      event.preventDefault();
      this.$store.dispatch('datasets/deleteDataset', uuid)
        .then(() => {
          this.$store.dispatch('collections/getCollection', this.uuid);
          this.deleteDsError = '';
        })
        .catch((error) => {
          this.deleteDsError = 'Deleting dataset failed (' + error + ')'
        });      
    },

      addPublication(event) {
      event.preventDefault();
      this.newProject.publications.push(this.newPublication);
      this.publication = '';
    },

    deletePublication(event, position) {
      event.preventDefault();
      this.newProject.publications.splice(position, 1);
    },

    addUserTag(event) {
      event.preventDefault();
      if (this.tagName !== '') {
        if (! Object.keys(this.newCollection.extra).includes(this.tagName)) {
          this.$set(this.newCollection.extra, this.tagName, '');
        }
      }
      this.tagName = '';
    },

    deleteUserTag(event, keyName) {
      event.preventDefault();
      this.$delete(this.newCollection.extra, keyName);
    },

    submitCollectionForm(event) {
      event.preventDefault();
      this.collectionToSubmit = JSON.parse(JSON.stringify(this.newCollection));
      this.$store.dispatch('collections/saveCollection', this.collectionToSubmit)
        .then(() => {
          this.$router.push({'name': 'Collection About', params: { 'uuid': this.uuid } });
        });
    },
    
    deleteCollection(event) {
      event.preventDefault();
      this.$store.dispatch('collections/deleteCollection', this.newCollection.id)
        .then(() => {
          this.$router.push({ 'name': 'Collection Browser' });
        });
    },

    cancelChanges(event) {
      event.preventDefault();
      if (this.newCollection.id !== '') 
        this.$router.push({ 'name': 'Collection About', params: { 'uuid': this.newCollection.id } });
      else
        this.$router.push({ 'name': 'Collection Browser' });
    },
    
  },
  
  mounted () {
    this.$store.dispatch('collections/getCollection', this.uuid)
      .then((response) => {
        this.newCollection = JSON.parse(JSON.stringify(response.data.project));
        this.newCollection.id = this.newCollection._id;
        delete this.newCollection._id;
        this.loading = false;
      })
      .catch(() => {
        this.loading = false;
        this.newCollection = {
          id: '',
          title: '',
          description: '',
          creator: '',
          receiver: '',
          extra: {}
        };
      });
    
    this.$store.dispatch('getCurrentUser', this.uuid)
      .then(() => {
        let sortFunc = (a, b) => {
          let aTitle = a.title.toUpperCase();
          let bTitle = b.title.toUpperCase();
          if (aTitle > bTitle) {
            return 1;
          }
          if (aTitle < bTitle) {
            return -1;
          }
          return 0;
        };
        if (this.currentUser.permissions.includes('DATA_MANAGEMENT')) {
          this.$store.dispatch('getDatasets')
            .then((response) => {
              this.availableDatasets = response.data.datasets;
              this.availableDatasets.sort(sortFunc);
            });
        }
        else {
          this.$store.dispatch('getCurrentUserDatasets')
            .then((response) => {
              this.availableDatasets = response.data.datasets;
              this.availableDatasets.sort(sortFunc);
            });
        }
      });
    if (this.user.permissions.includes('DATA_MANAGEMENT')) {
      this.$store.dispatch('getDatasets')
        .then((response) => {
          this.availableDatasets = response.data.datasets;
          this.availableDatasets.sort(sortFunc);
        });
    }
    else {
      this.$store.dispatch('getCurrentUserDatasets')
        .then((response) => {
          this.availableDatasets = response.data.datasets;
          this.availableDatasets.sort(sortFunc);
        });
    }
  }
}
</script>
