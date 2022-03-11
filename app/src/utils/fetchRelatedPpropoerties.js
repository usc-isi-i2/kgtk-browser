const fetchRelatedProperties = (id, property, skip=0, limit=10) => {

  let url =
    `/kb/rproperty?id=${id}&property=${property}&skip=${skip}&limit=${limit}`
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

export default fetchRelatedProperties
