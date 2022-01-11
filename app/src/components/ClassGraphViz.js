import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Grid from '@material-ui/core/Grid'


import fetchClassGraphData from '../utils/fetchClassGraphData'


const ClassGraphViz = () => {

  const { id } = useParams()

  const [data, setData] = useState({})

  useEffect(() => {
    fetchClassGraphData(id).then(data => {
      setData(data)
    })
  }, [])

  return (
    <Grid container spacing={1}>
    </Grid>
  )
}


export default ClassGraphViz
