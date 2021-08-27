const search = q => {

  const url = `/kb/query?q=${q}`

  return new Promise((resolve, reject) => {
    fetch(url, {method: 'GET'})
    .then(response => response.json())
    .then(response => resolve(response.matches))
    .catch(err => reject(err))
  })
}

export default search
