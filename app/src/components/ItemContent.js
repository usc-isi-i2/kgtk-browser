import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'
import { useParams } from 'react-router-dom'

import Data from './Data'
import Header from './Header'
import ArrowUp from './ArrowUp'
import fetchData from '../utils/fetchData'


const ItemContent = () => {

  const { id } = useParams()

  const [data, setData] = useState()
  const [loading, setLoading] = useState()

  useEffect(() => {
    getData(id)
  }, [])

  const getData = itemid => {
    setLoading(true)
    fetchData(itemid).then(data => {
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


export default ItemContent
