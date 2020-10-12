export function UPDATE_ENTRY (state, payload) {
  state.entry = payload;
}


export function UPDATE_ENTRY_FIELDS (state, payload) {
  let key = '';
  for (key in payload) {
    state.entry[key] = payload[key];
  }
}

export function UPDATE_STD_TAGS (state, payload) {
  let key = '';
  for (key in payload) {
    state.entry['tagsStandard'][key] = payload[key];
  }
}

export function UPDATE_USER_TAGS (state, payload) {
  let key = '';
  for (key in payload) {
    state.entry['tagsUser'][key] = payload[key];
  }
}

export function UPDATE_ENTRY_LIST (state, payload) {
  state.entryList = payload;
}


export function RESET_ENTRY (state) {
  state.entry = {};
}


export function RESET_ENTRY_LIST (state) {
  state.entryList = [];
}
