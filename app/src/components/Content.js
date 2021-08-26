import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles'


import Data from './Data'
import Logo from './Logo'
import ArrowUp from './ArrowUp'
import fetchData from '../utils/fetchData'


const useStyles = makeStyles(theme => ({
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
    <Container maxWidth="xl">
      <div id="top" />
      <Typography component="h3" variant="h3" className={classes.header}>
        <a href="https://github.com/usc-isi-i2/kgtk" title="Knowledge Graph Toolkit" rel="noopener noreferrer nofollow" target="_blank">
          <div className={ classes.logo }>
            <Logo/>
          </div>
        </a>
        KGTK Browser
      </Typography>
      {!!data && <Data data={data} />}
      <ArrowUp/>
    </Container>
  )
}


export default Content
