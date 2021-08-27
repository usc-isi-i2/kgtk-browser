import React from 'react'
import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import ImageList from '@material-ui/core/ImageList'
import ImageListItem from '@material-ui/core/ImageListItem'
import ImageListItemBar from '@material-ui/core/ImageListItemBar'
import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    paddingTop: theme.spacing(3),
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(4),
    paddingBottom: theme.spacing(2),
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    borderRadius: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
    color: '#fefefe',
  },
  link: {
    display: 'inline-block',
    padding: theme.spacing(1),
    textDecoration: 'underline',
    color: '#fefefe',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
    },
  },
  link2: {
    display: 'inline-block',
    paddingLeft: theme.spacing(3),
    color: '#fefefe',
    textDecoration: 'underline',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
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
  lang: {
    color: '#d4d4d4',
    marginLeft: theme.spacing(1),
  },
  row: {
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(1),
    borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
  },
  imageList: {
    flexWrap: 'nowrap',
    // Promote the list into his own layer on Chrome.
    // This cost memory but helps keeping high FPS.
    transform: 'translateZ(0)',
  },
  imageItem: {
    width: '50%',
    height: '300px',
  },
  title: {
    color: '#fefefe',
  },
  titleBar: {
    background:
      'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
  },
}))


const Data = ({ data }) => {

  const classes = useStyles()

  const renderDescription = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h4">{data.text}</Typography>
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
          <Typography variant="h4">Properties</Typography>
          {data.properties.map((property, index) => (
            <Grid container key={index}
              className={classes.row}>
              <Grid item xs={3}>
                {property.url || property.ref ? (
                  <Link variant='body1'
                    className={classes.link}
                    href={property.url ? property.url : `/?id=${property.ref}`}
                    title={property.url ? property.url : `/?id=${property.ref}`}>
                    {property.property}
                  </Link>
                ) : (
                  <Typography variant='body1'
                    className={classes.text}>
                    {property.property}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={9}>
                {!!property.values && property.values.map((value, index) => (
                  <Grid container key={index}>
                    <Grid item xs={12}>
                      {value.url || value.ref ? (
                        <Link variant='body1'
                          className={classes.link}
                          href={value.url ? value.url : `/?id=${value.ref}`}
                          title={value.url ? value.url : `/?id=${value.ref}`}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography variant='body1'
                          className={classes.text}>
                          {value.text}
                          {value.lang && (
                            <span className={classes.lang}>
                              [{value.lang}]
                            </span>
                          )}
                        </Typography>
                      )}
                      {!!value.qualifiers && value.qualifiers.map((qualifier, index) => (
                        <Grid container spacing={3} key={index}>
                          <Grid item xs={4}>
                            {qualifier.url || qualifier.ref ? (
                              <Link variant='body2'
                                className={classes.link2}
                                href={qualifier.url ? qualifier.url : `/?id=${qualifier.ref}`}
                                title={qualifier.url ? qualifier.url : `/?id=${qualifier.ref}`}>
                                {qualifier.property}
                              </Link>
                            ) : (
                              <Typography variant='body2'
                                className={classes.text2}>
                                {qualifier.text}
                                {qualifier.lang && (
                                  <span className={classes.lang}>
                                    [{qualifier.lang}]
                                  </span>
                                )}
                              </Typography>
                            )}
                          </Grid>
                          <Grid item xs={8}>
                            {!!qualifier.values && qualifier.values.map((value, index) => (
                              <Grid container key={index}>
                                {value.url || value.ref ? (
                                  <Link variant='body2'
                                    className={classes.link2}
                                    href={value.url ? value.url : `/?id=${value.ref}`}
                                    title={value.url ? value.url : `/?id=${value.ref}`}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography variant='body2'
                                    className={classes.text2}>
                                    {value.text}
                                    {value.lang && (
                                      <span className={classes.lang}>
                                        [{value.lang}]
                                      </span>
                                    )}
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
          <ImageList className={classes.imageList}
            rowHeight={350}
            cols={1.25} gap={15}>
            {data.gallery.map((image, index) => (
              <ImageListItem key={index}>
                <img src={image.url} alt={image.text} />
                <ImageListItemBar
                  title={image.text}
                  classes={{
                    root: classes.titleBar,
                    title: classes.title,
                  }}
                />
              </ImageListItem>
            ))}
          </ImageList>
        </Paper>
      </Grid>
    )
  }

  const renderIdentifiers = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h4">Identifiers</Typography>
          {data.xrefs.map((property, index) => (
            <Grid container key={index}
              className={classes.row}>
              <Grid item xs={6}>
                {property.url || property.ref ? (
                  <Link variant='body1'
                    className={classes.link}
                    href={property.url ? property.url : `/?id=${property.ref}`}
                    title={property.url ? property.url : `/?id=${property.ref}`}>
                    {property.property}
                  </Link>
                ) : (
                  <Typography variant='body1'
                    className={classes.text}>
                    {property.property}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={6}>
                {!!property.values && property.values.map((value, index) => (
                  <Grid container key={index}>
                    <Grid item xs={12}>
                      {value.url || value.ref ? (
                        <Link variant='body1'
                          className={classes.link}
                          href={value.url ? value.url : `/?id=${value.ref}`}
                          title={value.url ? value.url : `/?id=${value.ref}`}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography variant='body1'
                          className={classes.text}>
                          {value.text}
                          {value.lang && (
                            <span className={classes.lang}>
                              [{value.lang}]
                            </span>
                          )}
                        </Typography>
                      )}
                      {!!value.qualifiers && value.qualifiers.map((qualifier, index) => (
                        <Grid container spacing={3} key={index}>
                          <Grid item xs={4}>
                            {qualifier.url || qualifier.ref ? (
                              <Link variant='body2'
                                className={classes.link2}
                                href={qualifier.url ? qualifier.url : `/?id=${qualifier.ref}`}
                                title={qualifier.url ? qualifier.url : `/?id=${qualifier.ref}`}>
                                {qualifier.property}
                              </Link>
                            ) : (
                              <Typography variant='body2'
                                className={classes.text2}>
                                {qualifier.text}
                                {qualifier.lang && (
                                  <span className={classes.lang}>
                                    [{qualifier.lang}]
                                  </span>
                                )}
                              </Typography>
                            )}
                          </Grid>
                          <Grid item xs={8}>
                            {!!qualifier.values && qualifier.values.map((value, index) => (
                              <Grid container key={index}>
                                {value.url || value.ref ? (
                                  <Link variant='body2'
                                    className={classes.link2}
                                    href={value.url ? value.url : `/?id=${value.ref}`}
                                    title={value.url ? value.url : `/?id=${value.ref}`}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography variant='body2'
                                    className={classes.text2}>
                                    {value.text}
                                    {value.lang && (
                                      <span className={classes.lang}>
                                        [{value.lang}]
                                      </span>
                                    )}
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
