import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'

import Data from './Data'
import Header from './Header'
import ArrowUp from './ArrowUp'
import fetchData from '../utils/fetchData'


const Content = () => {

  const [data, setData] = useState()
  const [loading, setLoading] = useState()

  useEffect(() => {
    const locationQuery = new URLSearchParams(window.location.search)
    if ( locationQuery.has('id') ) {
      getData(locationQuery.get('id'))
    }
  }, [])

  const getData = id => {
    setLoading(true)
    fetchData(id).then(data => {
      setLoading(false)
      setData(data)
    })
  }

  return (
    <React.Fragment>
      <div id="top" />
      <Header getData={getData} />
      <Container maxWidth="xl">
        {!!data && <Data data={data} />}
        <ArrowUp/>
      </Container>
    </React.Fragment>
  )
}


export default Content
