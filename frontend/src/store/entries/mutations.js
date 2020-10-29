import Vue from 'vue'

export function UPDATE_ENTRY (state, payload) {
  state.entry = payload;
}


export function UPDATE_ENTRY_LOG (state, payload) {
  state.logs = payload;
}


export function UPDATE_ENTRY_FIELDS (state, payload) {
  let key = '';
  for (key in payload) {
    Vue.set(state.entry, key, payload[key]);
    state.entry[key] = payload[key];
  }
}


// expects payLoad: {'propertyName': propertyName, 'key': keyName}
export function ADD_PROPERTY (state, payload) {
  Vue.set(state.entry[payload.propertyName], payload.key, '');
}

// expects payLoad: {'propertyName': propertyName, 'value': propertyObject}
export function UPDATE_PROPERTY (state, payload) {
  let key = Object.keys(payload.value)[0];
  state.entry[payload.propertyName][key] = payload.value[key];
}

// expects payLoad: {'propertyName': propertyName, 'key': keyName}
export function DELETE_PROPERTY (state, payload) {
  Vue.delete(state.entry[payload.propertyName], payload.key);
}


export function UPDATE_ENTRY_LIST (state, payload) {
  state.entryList = payload;
}


export function RESET_ENTRY (state) {
  state.entry = {};
}


export function RESET_ENTRY_LOG (state) {
  state.logs = [];
}


export function RESET_ENTRY_LIST (state) {
  state.entryList = [];
}
