const fetchData = id => {

  const url = `/kb/item?fmt=cjson&id=${id}`

  return new Promise((resolve, reject) => {
    fetch(url, {method: 'GET'})
    .then(response => response.json())
    .then(data => resolve(data))
    .catch(err => reject(err))
  })
}

export default fetchData
