import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'


import Data from './Data'
import Header from './Header'
import ArrowUp from './ArrowUp'
import fetchData from '../utils/fetchData'


const Content = () => {

  const [data, setData] = useState()

  useEffect(() => {
    const locationQuery = new URLSearchParams(window.location.search)
    if ( locationQuery.has('id') ) {
      getData(locationQuery.get('id'))
    }
  }, [])

  const getData = id => {
    fetchData(id).then(data => setData(data))
  }

  return (
    <Container maxWidth="xl" disableGutters={true}>
      <div id="top" />
      <Header getData={getData} />
      {!!data && <Data data={data} />}
      <ArrowUp/>
    </Container>
  )
}


export default Content
