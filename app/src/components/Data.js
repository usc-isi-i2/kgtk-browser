import React from 'react'
import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import ImageList from '@material-ui/core/ImageList'
import ImageListItem from '@material-ui/core/ImageListItem'
import ImageListItemBar from '@material-ui/core/ImageListItemBar'

import useStyles from '../styles/data'
import classNames from '../utils/classNames'


const Data = ({ data }) => {

  const classes = useStyles()

  const getURL = item => {

    // if there is an external url, return url that right away
    if ( item.url ) {
      return item.url
    }

    // if there is no external url, link internally to `/kb/item/<node_id>`
    let url = `/kb/item/${item.ref}`

    // prefix the url with the location of where the app is hosted
    if ( process.env.PUBLIC_URL ) {
      url = `${process.env.PUBLIC_URL}${url}`
    }

    return url
  }

  const renderDescription = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h4" className={classes.title}>
            {data.text}
          </Typography>
          <Typography variant="subtitle1" className={classes.nodeId}>
            ({data.ref})
          </Typography>
          <Typography variant="subtitle2" className={classes.aliases}>
            {data.aliases.join(' | ')}
          </Typography>
          <Typography variant="subtitle1" className={classes.description}>
            {data.description}
          </Typography>
        </Paper>
      </Grid>
    )
  }

  const renderProperties = () => {
    return (
      <Grid item xs={12}>
        <Paper className={classes.paper}>
          <Typography variant="h6" className={classes.heading}>
            Properties
          </Typography>
          {data.properties.map((property, index) => (
            <Grid container key={index} className={classes.row} spacing={0}>
              <Grid item xs={3}>
                {property.url || property.ref ? (
                  <Link
                    variant="body2"
                    className={
                      classNames(classes.link, {
                        property: true,
                        externalLink: !!property.url,
                      })
                    }
                    href={getURL(property)}
                    title={property.url ? property.url : property.property}>
                    {property.property}
                  </Link>
                ) : (
                  <Typography
                    variant="body2"
                    title={property.property}
                    className={classes.text}>
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
                            title={value.text}
                            className={classes.text}>
                            {value.text}
                          </Typography>
                          <Link
                            variant="body2"
                            className={
                              classNames(classes.link, {
                                property: !!value.ref && value.ref[0] === 'P',
                                item: !!value.ref && value.ref[0] === 'Q',
                                externalLink: !!value.url,
                              })
                            }
                            href={getURL(value)}
                            title={value.url ? value.url : value.text}>
                            {value.units}
                          </Link>
                        </React.Fragment>
                      ) : value.url || value.ref ? (
                        <Link
                          variant="body2"
                          className={
                            classNames(classes.link, {
                              indent: false,
                              property: !!value.ref && value.ref[0] === 'P',
                              item: !!value.ref && value.ref[0] === 'Q',
                              externalLink: !!value.url,
                            })
                          }
                          href={getURL(value)}
                          title={value.url ? value.url : value.text}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography
                          variant="body2"
                          title={value.text}
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
                        <Grid container spacing={0} key={index}>
                          <Grid item xs={4}>
                            {qualifier.url || qualifier.ref ? (
                              <Link
                                variant="body2"
                                className={
                                  classNames(classes.link, {
                                    indent: true,
                                    smaller: true,
                                    property: true,
                                    externalLink: !!value.url,
                                  })
                                }
                                href={getURL(qualifier)}
                                title={qualifier.url ? qualifier.url : qualifier.property}>
                                {qualifier.property}
                              </Link>
                            ) : (
                              <Typography
                                variant="body2"
                                title={qualifier.text}
                                className={
                                  classNames(classes.text, {
                                    indent: true,
                                    smaller: true,
                                    property: true,
                                  })
                                }>
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
                                      title={value.text}
                                      className={
                                        classNames(classes.text, {
                                          smaller: true,
                                        })
                                      }>
                                      {value.text}
                                    </Typography>
                                    <Link
                                      variant="body2"
                                      className={
                                        classNames(classes.link, {
                                          property: !!value.ref && value.ref[0] === 'P',
                                          item: !!value.ref && value.ref[0] === 'Q',
                                          externalLink: !!value.url,
                                          smaller: true,
                                        })
                                      }
                                      href={getURL(value)}
                                      title={value.url ? value.url : value.units}>
                                      {value.units}
                                    </Link>
                                  </React.Fragment>
                                ) : value.url || value.ref ? (
                                  <Link
                                    variant="body2"
                                    className={
                                      classNames(classes.link, {
                                        indent: false,
                                        smaller: true,
                                        property: !!value.ref && value.ref[0] === 'P',
                                        item: !!value.ref && value.ref[0] === 'Q',
                                        externalLink: !!value.url,
                                      })
                                    }
                                    href={getURL(value)}
                                    title={value.url ? value.url : value.text}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography
                                    variant="body2"
                                    title={value.text}
                                    className={
                                      classNames(classes.text, {
                                        smaller: true,
                                      })
                                    }>
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
                    root: classes.imageTitleBar,
                    title: classes.imageTitle,
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
          <Typography variant="h4" className={classes.heading}>
            Identifiers
          </Typography>
          {data.xrefs.map((property, index) => (
            <Grid container key={index} className={classes.row}>
              <Grid item xs={6}>
                {property.url || property.ref ? (
                  <Link
                    variant="body2"
                    className={
                      classNames(classes.link, {
                        smaller: true,
                        identifier: true,
                        externalLink: !!property.url,
                      })
                    }
                    href={getURL(property)}
                    title={property.url ? property.url : property.property}>
                    {property.property}
                  </Link>
                ) : (
                  <Typography
                    variant="body2"
                    title={property.property}
                    className={
                      classNames(classes.text, {
                        smaller: true,
                      })
                    }>
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
                          className={
                            classNames(classes.link, {
                              smaller: true,
                              externalLink: !!value.url,
                            })
                          }
                          href={getURL(value)}
                          title={value.url ? value.url : value.text}>
                          {value.text}
                        </Link>
                      ) : (
                        <Typography
                          variant="body2"
                          title={value.text}
                          className={
                            classNames(classes.text, {
                              smaller: true,
                            })
                          }>
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
                          <Grid item xs={6}>
                            {qualifier.url || qualifier.ref ? (
                              <Link
                                variant="body2"
                                className={
                                  classNames(classes.link, {
                                    indent: true,
                                    smaller: true,
                                    externalLink: !!value.url,
                                  })
                                }
                                href={getURL(qualifier)}
                                title={qualifier.url ? qualifier.url : qualifier.property}>
                                {qualifier.property}
                              </Link>
                            ) : (
                              <Typography
                                variant="body2"
                                title={qualifier.text}
                                className={
                                  classNames(classes.text, {
                                    indent: true,
                                    smaller: true,
                                  })
                                }>
                                {qualifier.text}
                                {qualifier.lang && (
                                  <span className={classes.lang}>
                                    [{qualifier.lang}]
                                  </span>
                                )}
                              </Typography>
                            )}
                          </Grid>
                          <Grid item xs={6}>
                            {!!qualifier.values && qualifier.values.map((value, index) => (
                              <Grid container key={index}>
                                {value.url || value.ref ? (
                                  <Link
                                    variant="body2"
                                    className={
                                      classNames(classes.link, {
                                        smaller: true,
                                        externalLink: !!value.url,
                                      })
                                    }
                                    href={getURL(value)}
                                    title={value.url ? value.url : value.text}>
                                    {value.text}
                                  </Link>
                                ) : (
                                  <Typography
                                    variant="body2"
                                    title={value.text}
                                    className={
                                      classNames(classes.text, {
                                        smaller: true,
                                      })
                                    }>
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
