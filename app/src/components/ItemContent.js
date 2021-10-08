import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'

import Data from './Data'
import Header from './Header'
import ArrowUp from './ArrowUp'
import fetchInfo from '../utils/fetchInfo'


const ItemContent = () => {

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
        <Data />
        <ArrowUp/>
      </Container>
    </React.Fragment>
  )
}


export default ItemContent
