import React from 'react'
import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(3),
    paddingTop: theme.spacing(3),
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(4),
    paddingBottom: theme.spacing(2),
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
    color: '#fefefe',
  },
  link: {
    display: 'inline-block',
    padding: theme.spacing(1),
    color: '#fefefe',
    transition: '0.2s background ease',
    '&:hover': {
      textDecoration: 'underline',
      cursor: 'pointer',
    },
  },
  link2: {
    display: 'inline-block',
    paddingLeft: theme.spacing(1),
    color: '#fefefe',
    transition: '0.2s background ease',
    '&:hover': {
      textDecoration: 'underline',
      cursor: 'pointer',
    },
  },
  text: {
    display: 'inline-block',
    padding: theme.spacing(1),
    color: '#fefefe',
    width: '100%',
  },
  text2: {
    display: 'inline-block',
    paddingLeft: theme.spacing(1),
    color: '#fefefe',
    width: '100%',
  },
  row: {
    paddingTop: theme.spacing(3),
    borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
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
          {data.properties.map((property, index) => (
            <Grid container spacing={3} key={index}
              className={classes.row}>
              <Grid item xs={3}>
                <Link variant='body1'
                  className={classes.link}
                  href={`/?id=${property.ref}`}>
                  {property.property}
                </Link>
              </Grid>
              <Grid item xs={9}>
                {!!property.values && property.values.map((value, index) => (
                  <Grid container spacing={3} key={index}>
                    <Grid item xs={12}>
                      {value.url || value.ref ? (
                        <Link variant='body1'
                          className={classes.link}
                          href={`/?id=${value.ref}`}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography variant='body1'
                          className={classes.text}>
                          {value.text}
                        </Typography>
                      )}
                      {!!value.qualifiers && value.qualifiers.map((qualifier, index) => (
                        <Grid container spacing={3} key={index}>
                          <Grid item xs={4}>
                            <Link variant='body2'
                              className={classes.link2}
                              href={`/?id=${qualifier.ref}`}>
                              {qualifier.property}
                            </Link>
                          </Grid>
                          <Grid item xs={8}>
                            {!!qualifier.values && qualifier.values.map((value, index) => (
                              <Grid container key={index}>
                                {value.url || value.ref ? (
                                  <Link variant='body2'
                                    className={classes.link2}
                                    href={value.url ? value.url : `/?id=${value.ref}`}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography variant='body2'
                                    className={classes.text2}>
                                    {value.text}
                                  </Typography>
                                )}
                              </Grid>
                            ))}
                          </Grid>
                        </Grid>
                      ))}
                    </Grid>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          ))}
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
          {data.xrefs.map((property, index) => (
            <Grid container spacing={3} key={index}
              className={classes.row}>
              <Grid item xs={6}>
                <Link variant='body1'
                  className={classes.link}
                  href={`/?id=${property.ref}`}>
                  {property.property}
                </Link>
              </Grid>
              <Grid item xs={6}>
                {!!property.values && property.values.map((value, index) => (
                  <Grid container spacing={3} key={index}>
                    <Grid item xs={12}>
                      {value.url || value.ref ? (
                        <Link variant='body1'
                          className={classes.link}
                          href={`/?id=${value.ref}`}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography variant='body1'
                          className={classes.text}>
                          {value.text}
                        </Typography>
                      )}
                      {!!value.qualifiers && value.qualifiers.map((qualifier, index) => (
                        <Grid container spacing={3} key={index}>
                          <Grid item xs={4}>
                            <Link variant='body2'
                              className={classes.link2}
                              href={`/?id=${qualifier.ref}`}>
                              {qualifier.property}
                            </Link>
                          </Grid>
                          <Grid item xs={8}>
                            {!!qualifier.values && qualifier.values.map((value, index) => (
                              <Grid container key={index}>
                                {value.url || value.ref ? (
                                  <Link variant='body2'
                                    className={classes.link2}
                                    href={value.url ? value.url : `/?id=${value.ref}`}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography variant='body2'
                                    className={classes.text2}>
                                    {value.text}
                                  </Typography>
                                )}
                              </Grid>
                            ))}
                          </Grid>
                        </Grid>
                      ))}
                    </Grid>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          ))}
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
