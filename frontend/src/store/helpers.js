export function getCsrfHeader() {
  let name = "_csrf_token=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return {'X-CSRFToken': c.substring(name.length, c.length)};
    }
  }
  return "";
}
