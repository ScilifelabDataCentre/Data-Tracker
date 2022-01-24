<template>
<q-page padding>
  <div class="text-h3 q-mb-lg">
    Not Authorised
  </div>

  <div class="text-h5">
    You do not have the required permissions to display the page.
  </div>

  <div v-if="Object.keys(toPath).length !== 0">
    Page: {{ toPath.name }} ({{ toPath.path }})
  </div>
  
  <q-btn class="q-mt-xl"
         color="white"
         text-color="blue"
         unelevated
         :to="{'name': fixedFrom.name}"
         :label="'Go back to ' + fixedFrom.name"
         no-caps />
</q-page>
</template>

<script >
export default {
  name: 'NonAuth',
  computed: {
    fixedFrom: {
      get () {
        if (!this.fromPath.name)
          return {name: "Home", path: "/"}
        else
          return this.fromPath
      }
    }
  },
  props: {
    toPath: {
      type: Object,
      default () {
        return {}
      }
    },
    fromPath: {
      type: Object,
      default () {
        return {"name": "Home",
                "path": "/"}
      }
    },
  },

}
</script>
