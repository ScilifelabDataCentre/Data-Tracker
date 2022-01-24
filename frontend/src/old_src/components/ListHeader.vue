<template>
<q-item-label header>
  <span>
    {{ title }}
    <q-tooltip>
      {{ explanation }}
    </q-tooltip>
  </span>
</q-item-label>
</template>

<script>
export default {
  name: 'ListHeader',

  props: {
    title: {
      type: String,
      required: true
    },
    explanation: {
      type: String,
      required: true
    },
  }
}
</script>
