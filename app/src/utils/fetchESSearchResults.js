const fetchESSearchResults = (q, is_class, instance_of) => {

  let url = `/api?&q=${ q }&type=ngram&extra_info=true&language=en&item=qnode`

  if (is_class === 'true') {
    url += `&is_class=true`
  }

  if ( instance_of ) {
    url += `&instance_of=${instance_of}`
  }

  if (process.env.REACT_APP_KGTK_SEARCH_ES_URL) {
    url = `${process.env.REACT_APP_KGTK_SEARCH_ES_URL}${ url }`
  } else {
    url = `https://kgtk.isi.edu${ url }`
  }

  return new Promise((resolve, reject) => {
    fetch(url, { method: 'GET' })
      .then(response => response.json())
      .then(response => resolve(response.map(result => createDict(result))))
      .catch(err => reject(err))
  })
}

function createDict (result) {
  return {
    'ref': result.qnode,
    'text': result.qnode,
    'description': result.label[0],
    'ref_description': result.description[0],
  }
}

export default fetchESSearchResults
