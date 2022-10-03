import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'

import Search from './Search'
import Header from './Header'
import ArrowUp from './ArrowUp'
import fetchInfo from '../utils/fetchInfo'


const Content = () => {

  const [info, setInfo] = useState()

  useEffect(() => {
    // get the project configuration information
    fetchInfo().then(info => setInfo(info))
  }, [])

  return (
    <React.Fragment>
      <div id="top" />
      <Header info={info} />
      <Container maxWidth="xl">
        <Search />
        <ArrowUp/>
      </Container>
    </React.Fragment>
  )
}


export default Content
