import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Grid from '@material-ui/core/Grid'
import CircularProgress from '@material-ui/core/CircularProgress'

import useStyles from '../styles/data'
import fetchClassGraphData from '../utils/fetchClassGraphData'


const ClassGraphViz = () => {

  const { id } = useParams()

  const classes = useStyles()

  const [data, setData] = useState({})
  const [loading, setLoading] = useState()

  useEffect(() => {
    setLoading(true)
    fetchClassGraphData(id).then(data => {
      setLoading(false)
      setData(data)
    })
  }, [])

  const renderLoading = () => {
    if ( !loading ) { return }
    return (
      <CircularProgress
        size={50}
        color="inherit"
        className={classes.loading} />
    )
  }

  return (
    <Grid container spacing={1}>
      {renderLoading()}
    </Grid>
  )
}


export default ClassGraphViz
