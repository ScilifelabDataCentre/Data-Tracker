export function setInfo (state, payload) {
  state.info = payload;
  state.infoLoaded = true;
}

export function setDatasets (state, payload) {
  state.datasets = payload;
}

export function setOrders (state, payload) {
  state.orders = payload;
}

export function setCollections (state, payload) {
  state.collections = payload;
}
