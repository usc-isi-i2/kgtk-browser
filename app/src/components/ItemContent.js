import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'
import { useParams } from 'react-router-dom'


import Data from './Data'
import Header from './Header'
import ArrowUp from './ArrowUp'
import fetchData from '../utils/fetchData'


const ItemContent = () => {

    const [data, setData] = useState()
    const { id } = useParams()

    useEffect(() => {
	getData(id)
  }, [])

    const getData = (itemid) => {
        fetchData(itemid).then(data => setData(data))
  }

  return (
    <Container maxWidth="xl">
      <div id="top" />
      <Header getData={getData} />
      {!!data && <Data data={data} />}
      <ArrowUp/>
    </Container>
  )
}


export default ItemContent
