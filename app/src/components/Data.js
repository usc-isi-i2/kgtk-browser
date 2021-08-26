import React from 'react'
import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(3),
    paddingTop: theme.spacing(6),
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(4),
    paddingBottom: theme.spacing(2),
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
  },
}))


const Data = ({ data }) => {

  const classes = useStyles()

  const renderDescription = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h2">{data.text}</Typography>
          <Typography variant="h6">{data.ref}</Typography>
          <Typography variant="h6">{data.description}</Typography>
        </Paper>
      </Grid>
    )
  }

  const renderProperties = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
        </Paper>
      </Grid>
    )
  }

  const renderGallery = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
        </Paper>
      </Grid>
    )
  }

  const renderIdentifiers = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
        </Paper>
      </Grid>
    )
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={8}>
        <Grid container spacing={3}>
          {renderDescription()}
          {renderProperties()}
        </Grid>
      </Grid>
      <Grid item xs={4}>
        <Grid container spacing={3}>
          {renderGallery()}
          {renderIdentifiers()}
        </Grid>
      </Grid>
    </Grid>
  )

}


export default Data
