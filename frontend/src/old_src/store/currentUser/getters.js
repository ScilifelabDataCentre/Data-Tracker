export function info (state) {
  return state.info;
}                  

export function orders (state) {
  return state.orders;
}

export function datasets (state) {
  return state.datasets;
}

export function collections (state) {
  return state.collections;
}

export function isLoggedIn (state) {
  return state.info._id !== ''
}

export function infoLoaded (state) {
  return state.infoLoaded
}
