<template>
<q-page padding>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>

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
      </q-card-section>
    </q-form>
  </q-card>
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
        extra: {},
      },

    }
  },
  
  mounted () {
    this.$store.dispatch('datasets/getDataset', this.uuid)
      .then(() => this.loading = false)
      .catch(() => this.loading = false);
    this.newDataset = this.origDataset;
    this.newDataset.id = this.newDataset._id;
    delete this.newDataset._id;
    delete this.newDataset.related;
    delete this.newDataset.projects;

  }

}
</script>
