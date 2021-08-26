import React, { useEffect, useState } from 'react'
import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles'


import Logo from './Logo'
import ArrowUp from './ArrowUp'
import fetchData from '../utils/fetchData'


const useStyles = makeStyles(theme => ({
  content: {
    width: '100vw',
    height: '100vh',
    background: 'linear-gradient(150deg, #708090, #002133)',
    backgroundAttachment: 'fixed',
    backgroundSize: '100% 150%',
  },
  header: {
    color: '#fefefe',
    marginTop: theme.spacing(3),
  },
  logo: {
    display: 'inline-block',
    verticalAlign: 'middle',
    width: theme.spacing(12),
    height: theme.spacing(12),
    marginRight: theme.spacing(2),
  },
}))


const Content = () => {

  const classes = useStyles()

  const [data, setData] = useState()

  useEffect(() => {
    const locationQuery = new URLSearchParams(window.location.search)
    if ( locationQuery.has('id') ) {
      const id = locationQuery.get('id')
      fetchData(id).then(data => setData(data))
    }
  }, [])

  return (
    <Grid className={classes.content}>
      <div id="top" />
      <Typography component="h3" variant="h3" className={classes.header}>
        <a href="https://github.com/usc-isi-i2/kgtk" title="Knowledge Graph Toolkit" rel="noopener noreferrer nofollow" target="_blank">
          <div className={ classes.logo }>
            <Logo/>
          </div>
        </a>
        KGTK Browser
      </Typography>

      <ArrowUp/>
    </Grid>
  )
}


export default Content
