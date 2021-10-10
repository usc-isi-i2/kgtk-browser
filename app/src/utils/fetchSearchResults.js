const fetchSearchResults = q => {

  let url = `/kb/query?q=${q}`
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
