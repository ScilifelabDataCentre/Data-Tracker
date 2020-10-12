export function UPDATE_ENTRY (state, payload) {
  state.entry = payload;
}


export function UPDATE_ENTRY_FIELDS (state, payload) {
  let key = '';
  for (key in payload) {
    state.entry[key] = payload[key];
  }
}


export function UPDATE_ENTRY_LIST (state, payload) {
  state.entryList = payload;
}


export function RESET_ENTRY (state, payload) {
  state.entry = {};
}


export function RESET_ENTRY_LIST (state, payload) {
  state.entryList = [];
}
