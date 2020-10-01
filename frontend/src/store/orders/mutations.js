export function updateOrder (state, payload) {
  state.order = payload;
}


export function updateOrderFields (state, payload) {
  let key = '';
  for (key in payload) {
    state.order[key] = payload[key];
  }
}


export function updateOrders (state, payload) {
  state.orders = payload;
}
