<template>
<q-page class="q-pa-sm">
  <div class="text-center q-mb-xl">
    <h1 class="text-h2">SciLifeLab Data Tracker</h1>
    <div class="text-h5">
      A system for tracking data generated by SciLifeLab facilities.
    </div>
  </div>
  <div class="row flex flex-center">
    <div class="col-md-4 col-lg-4 col-xs-10 col-sm-10">
      <q-card class="q-pa-lg text-center box-shadow q-ma-md">
	<q-card-section>
          <q-icon size="150px" name="fas fa-chart-area" style="color: #045C64;"/>
          <div class="text-h5 text-weight-bold">Datasets</div>
        </q-card-section>
	<q-card-section class="q-pt-none">
	  <q-btn
            flat
            dense
	    to="/datasets"
            label="Browse Datasets" />
	</q-card-section>
      </q-card>
    </div>
    <div class="col-md-4 col-lg-4 col-xs-10 col-sm-10">
      <q-card class="q-pa-lg text-center box-shadow q-ma-md">
	<q-card-section>
          <q-icon size="150px" name="fas fa-layer-group" style="color: #045C64;" />

          <div class="text-h5 text-weight-bold">Collections</div>
        </q-card-section>
	<q-card-section class="q-pt-none">
	  <q-btn
            flat
            dense
	    to="/collections"
            label="Browse Collections" />
	</q-card-section>

      </q-card>
    </div>
  </div>
</q-page>
</template>

<script>
export default {
  name: 'PageIndex',

  data () {
    return {
    }
  }
}
</script>
