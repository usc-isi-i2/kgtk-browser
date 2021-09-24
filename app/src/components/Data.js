import React from 'react'
import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import ImageList from '@material-ui/core/ImageList'
import ImageListItem from '@material-ui/core/ImageListItem'
import ImageListItemBar from '@material-ui/core/ImageListItemBar'

import useStyles from '../styles/data'


const Data = ({ data }) => {

  const classes = useStyles()

  const renderDescription = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h6">{data.text}</Typography>
          <Typography variant="subtitle2">{data.ref}</Typography>
          <Typography variant="subtitle2">{data.aliases.join(' | ')}</Typography>
          <Typography variant="subtitle2">{data.description}</Typography>
        </Paper>
      </Grid>
    )
  }

  const renderProperties = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h6">Properties</Typography>
          {data.properties.map((property, index) => (
            <Grid container key={index} className={classes.row} spacing={0}>
              <Grid item xs={3}>
                {property.url || property.ref ? (
                  <Link
                    variant="body2"
                    className={classes.link}
                    href={property.url ? property.url : `/kb/item/${property.ref}`}
                    title={property.url ? property.url : `/kb/item/${property.ref}`}>
                    {property.property}
                  </Link>
                ) : (
                  <Typography variant="body2" className={classes.text}>
                    {property.property}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={9}>
                {!!property.values && property.values.map((value, index) => (
                  <Grid container key={index} spacing={0}>
                    <Grid item xs={12}>
                      {value.units ? (
                        <React.Fragment>
                          <Typography
                            variant="body2"
                            component="span"
                            className={classes.text4}>
                            {value.text}&nbsp;
                          </Typography>
                          <Link
                            variant="body2"
                            className={classes.link4}
                            href={value.url ? value.url : `/kb/item/${value.ref}`}
                            title={value.url ? value.url : `/kb/item/${value.ref}`}>
                            {value.units}
                          </Link>
                        </React.Fragment>
                      ) : value.url || value.ref ? (
                        <Link
                          variant="body2"
                          className={classes.link}
                          href={value.url ? value.url : `/kb/item/${value.ref}`}
                          title={value.url ? value.url : `/kb/item/${value.ref}`}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography variant="body2" className={classes.text}>
                          {value.text}
                          {value.lang && (
                            <span className={classes.lang}>
                              [{value.lang}]
                            </span>
                          )}
                        </Typography>
                      )}
                      {!!value.qualifiers && value.qualifiers.map((qualifier, index) => (
                        <Grid container spacing={0} key={index}>
                          <Grid item xs={4}>
                            {qualifier.url || qualifier.ref ? (
                              <Link
                                variant="body2"
                                className={classes.link2}
                                href={qualifier.url ? qualifier.url : `/kb/item/${qualifier.ref}`}
                                title={qualifier.url ? qualifier.url : `/kb/item/${qualifier.ref}`}>
                                {qualifier.property}
                              </Link>
                            ) : (
                              <Typography variant="body2" className={classes.text2}>
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
                              <Grid item key={index}>
                                {value.units ? (
                                  <React.Fragment>
                                    <Typography
                                      variant="body2"
                                      component="span"
                                      className={classes.text4}>
                                      {value.text}&nbsp;
                                    </Typography>
                                    <Link
                                      variant="body2"
                                      className={classes.link4}
                                      href={value.url ? value.url : `/kb/item/${value.ref}`}
                                      title={value.url ? value.url : `/kb/item/${value.ref}`}>
                                      {value.units}
                                    </Link>
                                  </React.Fragment>
                                ) : value.url || value.ref ? (
                                  <Link
                                    variant="body2"
                                    className={classes.link}
                                    href={value.url ? value.url : `/kb/item/${value.ref}`}
                                    title={value.url ? value.url : `/kb/item/${value.ref}`}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography variant="body2" className={classes.text}>
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
          <ImageList
            rowHeight={350}
            cols={1.25} gap={15}
            className={classes.imageList}>
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
            <Grid container key={index} className={classes.row}>
              <Grid item xs={6}>
                {property.url || property.ref ? (
                  <Link
                    variant="body2"
                    className={classes.link3}
                    href={property.url ? property.url : `/?id=${property.ref}`}
                    title={property.url ? property.url : `/?id=${property.ref}`}>
                    {property.property}
                  </Link>
                ) : (
                  <Typography variant="body2" className={classes.text3}>
                    {property.property}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={6}>
                {!!property.values && property.values.map((value, index) => (
                  <Grid container key={index}>
                    <Grid item xs={12}>
                      {value.url || value.ref ? (
                        <Link
                          variant="body2"
                          className={classes.link3}
                          href={value.url ? value.url : `/?id=${value.ref}`}
                          title={value.url ? value.url : `/?id=${value.ref}`}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography variant="body2" className={classes.text3}>
                          {value.text}
                          {value.lang && (
                            <span className={classes.lang}>
                              [{value.lang}]
                            </span>
                          )}
                        </Typography>
                      )}
                      {!!value.qualifiers && value.qualifiers.map((qualifier, index) => (
                        <Grid container spacing={0} key={index}>
                          <Grid item xs={4}>
                            {qualifier.url || qualifier.ref ? (
                              <Link
                                variant="body2"
                                className={classes.link2}
                                href={qualifier.url ? qualifier.url : `/?id=${qualifier.ref}`}
                                title={qualifier.url ? qualifier.url : `/?id=${qualifier.ref}`}>
                                {qualifier.property}
                              </Link>
                            ) : (
                              <Typography variant="body2" className={classes.text2}>
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
                                  <Link
                                    variant="body2"
                                    className={classes.link2}
                                    href={value.url ? value.url : `/?id=${value.ref}`}
                                    title={value.url ? value.url : `/?id=${value.ref}`}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography variant="body2" className={classes.text2}>
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
    <Grid container spacing={1}>
      <Grid item xs={8}>
        <Grid container spacing={1}>
          {renderDescription()}
          {renderProperties()}
        </Grid>
      </Grid>
      <Grid item xs={4}>
        <Grid container spacing={1}>
          {renderGallery()}
          {renderIdentifiers()}
        </Grid>
      </Grid>
    </Grid>
  )
}


export default Data
