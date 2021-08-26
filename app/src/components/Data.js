import React from 'react'
import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'


const Data = ({ data }) => {

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h2">{data.text}</Typography>
        <Typography variant="h6">{data.ref}</Typography>
        <Typography variant="h6">{data.description}</Typography>
      </Grid>
    </Grid>
  )

}


export default Data
