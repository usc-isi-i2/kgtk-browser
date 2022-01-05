const fetchESSearchResults = q => {

  let url = `/api?&q=${ q }&type=ngram&extra_info=true&language=en&item=qnode`

  if (process.env.KGTK_SEARCH_ES_URL) {
    url = `${ process.env.KGTK_SEARCH_ES_URL }${ url }`
  } else {
    url = `https://kgtk.isi.edu${ url }`
  }

  return new Promise((resolve, reject) => {
    fetch(url, { method: 'GET' }).
      then(response => response.json()).
      then(response => resolve(response.map(result => createDict(result)))).
      catch(err => reject(err))
  })
}

function createDict (result) {
  var d = {}
  d['ref'] = result.qnode
  d['text'] = result.qnode
  d['description'] = result.label[0]
  d['ref_description'] = result.description[0]
  return d
}

export default fetchESSearchResults
