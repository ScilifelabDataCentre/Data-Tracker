
export function UPDATE_ENTRY (state, payload) {
  state.entry = payload;
}


export function UPDATE_ENTRY_LOG (state, payload) {
  state.logs = payload;
}


export function UPDATE_USER_ACTIONS (state, payload) {
  state.actions = payload;
}


export function UPDATE_ENTRY_FIELDS (state, payload) {
  let key = '';
  for (key in payload) {
    state.entry[key] = payload[key];
  }
}


// expects payLoad: {'propertyName': propertyName, 'key': keyName}
export function ADD_PROPERTY (state, payload) {
  state.entry[payload.propertyName][payload.key] = '';
}

// expects payLoad: {'propertyName': propertyName, 'value': propertyObject}
export function UPDATE_PROPERTY (state, payload) {
  let key = Object.keys(payload.value)[0];
  state.entry[payload.propertyName][key] = payload.value[key];
}

// expects payLoad: {'propertyName': propertyName, 'key': keyName}
export function DELETE_PROPERTY (state, payload) {
  delete state.entry[payload.propertyName][payload.key];
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


export function RESET_USER_ACTIONS (state) {
  state.actions = [];
}


export function RESET_ENTRY_LIST (state) {
  state.entryList = [];
}


export function SET_PARENT_ORDER (state, payload) {
  state.parentOrder = payload;
}
