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
      </q-card-section>

      <q-card-section>
        <q-table
          title="Datasets"
          :data="datasetList"
          :columns="columns"
          row-key="_id"
          :pagination.sync="pagination"
          no-data-label="No entries found"
          :no-results-label="datasetFilter + ' does not match any entries'"
          :loading="loadingDatasets"
          selection="multiple"
          :selected.sync="newCollection.datasets"
          :filter="datasetFilter"
          >
          <template v-slot:top-right>
            <q-toggle v-model="showOnlySelectedDatasets"
                      label="Only selected"
                      left-label>
            </q-toggle>
            <q-input rounded outlined dense debounce="300" v-model="datasetFilter" placeholder="Search">
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
          </template>
        </q-table>

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
                       @click="deletePublication($event, i)" />
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
                   v-model="tagName">
            <template v-slot:append>
              <q-btn round color="positive" icon="add" @click="addUserTag"/>
            </template>
          </q-input>
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

  watch: {
    'showOnlySelectedDatasets' () {
      if (this.showOnlySelectedDatasets)
        this.datasetList = this.newCollection.datasets;
      else
        this.datasetList = this.availableDatasets;
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
        contact: '',
        publications: '',
        datasets: '',
        extra: {},
      },
      loadingDatasets: true,
      availableDatasets: [],
      datasetList: [],
      showOnlySelectedDatasets: false,

      newPublication: '',
      tagName: '',

      pagination: {
        rowsPerPage: 10
      },
      selected: [],
      datasetFilter: '',
      columns: [
        {
          name: 'id',
          label: 'Identifier (UUID)',
          field: '_id',
          required: true,
          align: 'left',
          sortable: true,
        },
        {
          name: 'title',
          label: 'Dataset title',
          field: 'title',
          required: true,
          sortable: true
        }
      ]

    }
  },

  methods: {
    dsFilter (val, update, abort) {
      update(() => {
        this.loadingDatasets = true;
        const needle = val.toLowerCase()
        this.filteredDatasets = this.availableDatasets.filter(ds => {
          return (ds.title.toLowerCase().indexOf(needle) > -1 ||
            ds._id.indexOf(needle) > -1);
        });
        this.loadingDatasets = false;
      })
    },

    addPublication(event) {
      event.preventDefault();
      this.newCollection.publications.push(this.newPublication);
      this.publication = '';
    },

    deletePublication(event, position) {
      event.preventDefault();
      this.newCollection.publications.splice(position, 1);
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

    getSelectedString () {
      return this.selected.length === 0 ? '' : `${this.selected.length} record${this.selected.length > 1 ? 's' : ''} selected of ${this.data.length}`
    }
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
    
    this.$store.dispatch('currentUser/getInfo', this.uuid)
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
          this.$store.dispatch('datasets/getDatasets')
            .then((response) => {
              this.availableDatasets = JSON.parse(JSON.stringify(response.data.datasets));
              this.availableDatasets.sort(sortFunc);
              Object.freeze(this.availableDatasets);
              this.datasetList = this.availableDatasets;
              this.loadingDatasets = false;
            });
        }
        else {
          this.$store.dispatch('currentUser/getDatasets')
            .then((response) => {
              this.availableDatasets = response.data.datasets;
              this.availableDatasets.sort(sortFunc);
              this.datasetList = this.availableDatasets;
              this.loadingDatasets = false;
            });
        }
      });
  }
}
</script>
