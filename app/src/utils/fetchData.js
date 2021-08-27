const fetchData = id => {

  let url = `/kb/item?fmt=cjson&id=${id}`
  if ( process.env.REACT_APP_BACKEND_URL ) {
    url = `${process.env.REACT_APP_BACKEND_URL}${url}`
  }

  return new Promise((resolve, reject) => {
    fetch(url, {method: 'GET'})
    .then(response => response.json())
    .then(data => resolve(data))
    .catch(err => reject(err))
  })
}

export default fetchData
