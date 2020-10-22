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
    state.entry[key] = payload[key];
  }
}


// expects payLoad: {'tagName': tagName, 'key': keyName}
export function ADD_TAG (state, payload) {
  Vue.set(state.entry[payload.tagName], payload.key, '');
}

// expects payLoad: {'tagName': tagName, 'value': tagObject}
export function UPDATE_TAG (state, payload) {
  let key = Object.keys(payload.value)[0];
  state.entry[payload.tagName][key] = payload.value[key];
}

// expects payLoad: {'tagName': tagName, 'key': keyName}
export function DELETE_TAG (state, payload) {
  Vue.delete(state.entry[payload.tagName], payload.key);
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
