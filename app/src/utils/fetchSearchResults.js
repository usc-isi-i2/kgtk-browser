const fetchSearchResults = (q, is_class, instance_of) => {

  let url = `/kb/query?q=${q}`
  if (is_class === 'true') {
    url += `&is_class=true`
  }

  if ( instance_of ) {
    url += `&instance_of=${instance_of}`
  }

  if ( process.env.REACT_APP_BACKEND_URL ) {
    url = `${process.env.REACT_APP_BACKEND_URL}${url}`
  }

  return new Promise((resolve, reject) => {
    fetch(url, {method: 'GET'})
    .then(response => response.json())
    .then(response => resolve(response.matches))
    .catch(err => reject(err))
  })
}

export default fetchSearchResults
