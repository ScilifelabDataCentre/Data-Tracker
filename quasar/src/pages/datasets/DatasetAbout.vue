<template>
<q-page padding>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
  <q-page-sticky position="bottom-right" :offset="[24, 24]">
    <q-btn fab icon="edit" color="accent" />
  </q-page-sticky>
      <div class="text-center q-mb-lg">
        <h1 class="text-h2 q-mb-xs ">{{ dataset.title }}</h1>
        <div class="text-subtitle1 text-italic">
          {{ dataset._id }}
        </div>
      </div>
  <q-card class="q-my-lg">
    <q-card-section>
      <q-markdown :src="dataset.description" />
    </q-card-section>
  </q-card>
  <q-card class="q-my-lg">
    <q-card-section>
      <q-markdown :src="dataset.extra" />
    </q-card-section>
  </q-card>
</q-page>
</template>

<script>
export default {
  name: 'DatasetAbout',
  props: ['uuid'],

  computed: {
    dataset: {
      get () {
        return this.$store.state.datasets.dataset;
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
