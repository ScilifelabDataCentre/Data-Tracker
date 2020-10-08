<template>
<q-page padding>
  <dataset-about />
</q-page>
</template>

<script>
import DatasetAbout from 'components/DatasetAbout.vue'

export default {
  name: 'DatasetInfo',

 components: {'dataset-about': UserInfo},
  
  props: {
    uuid: {
      type: String,
      required: true
    }
  },

  computed: {
    dataset: {
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
    }
  },
  
  mounted () {
    this.$store.dispatch('datasets/getDataset', this.uuid)
      .then(() => this.loading = false)
      .catch(() => this.loading = false)
  }
  
}
</script>

