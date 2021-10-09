import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import useBreadcrumbs from 'use-react-router-breadcrumbs'
import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import ImageList from '@material-ui/core/ImageList'
import ImageListItem from '@material-ui/core/ImageListItem'
import ImageListItemBar from '@material-ui/core/ImageListItemBar'
import ExpansionPanel from '@material-ui/core/ExpansionPanel'
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary'
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore'
import CircularProgress from '@material-ui/core/CircularProgress'

import routes from '../utils/routes'
import useStyles from '../styles/data'
import fetchData from '../utils/fetchData'
import classNames from '../utils/classNames'


const Data = () => {

  const { id } = useParams()

  const classes = useStyles()

  const breadcrumbs = useBreadcrumbs(routes)

  const [data, setData] = useState({})
  const [loading, setLoading] = useState()

  useEffect(() => {
    setLoading(true)
    fetchData(id).then(data => {
      setLoading(false)
      setData(data)
    })
  }, [id])

  const getURL = item => {

    // if there is an external url, return url that right away
    if ( item.url ) {
      return item.url
    }

    // if there is no external url, link internally to `/kb/item/<node_id>`
    let url = `/browser/${item.ref}`

    // prefix the url with the location of where the app is hosted
    if ( process.env.REACT_APP_FRONTEND_URL ) {
      url = `${process.env.REACT_APP_FRONTEND_URL}${url}`
    }

    return url
  }

  const renderBreadcrumbs = () => {
    return (
      <Grid item xs={12}>
        {breadcrumbs.map(({ match, breadcrumb }) => {
          return (
            <React.Fragment>
              {match.url !== '/' && (
                <span className={classes.breadcrumbArrow}> > </span>
              )}
              <span key={match.url} className={
                classNames(classes.link, {
                  breadcrumb: true,
                })
              }>
                <Link to={match.url}>{breadcrumb}</Link>
              </span>
            </React.Fragment>
          )
        })}
      </Grid>
    )
  }

  const renderLoading = () => {
    if ( !loading ) { return }
    return (
      <CircularProgress
        size={50}
        color="inherit"
        className={classes.loading} />
    )
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
          {data.aliases && (
            <Typography variant="subtitle2" className={classes.aliases}>
              {data.aliases.join(' | ')}
            </Typography>
          )}
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
        <ExpansionPanel
          square={true}
          defaultExpanded={true}
          TransitionProps={{ timeout: 0 }}>
          <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" className={classes.heading}>
              Properties
            </Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails className={classes.paper}>
            {data.properties && data.properties.map((property, index) => (
              <Grid container key={index} className={classes.row} spacing={0}>
                <Grid item xs={3}>
                  {property.url || property.ref ? (
                    <Link
                      className={
                        classNames(classes.link, {
                          property: true,
                          externalLink: !!property.url,
                        })
                      }
                      to={{ pathname: getURL(property) }}
                      target={!!property.url ? '_blank' : ''}
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
                              className={
                                classNames(classes.link, {
                                  property: !!value.ref && value.ref[0] === 'P',
                                  item: !!value.ref && value.ref[0] === 'Q',
                                  externalLink: !!value.url,
                                })
                              }
                              to={{ pathname: getURL(value) }}
                              target={!!value.url ? '_blank' : ''}
                              title={value.url ? value.url : value.text}>
                              {value.units}
                            </Link>
                          </React.Fragment>
                        ) : value.url || value.ref ? (
                          <Link
                            className={
                              classNames(classes.link, {
                                indent: false,
                                property: !!value.ref && value.ref[0] === 'P',
                                item: !!value.ref && value.ref[0] === 'Q',
                                externalLink: !!value.url,
                              })
                            }
                            to={{ pathname: getURL(value) }}
                            target={!!value.url ? '_blank' : ''}
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
                                  className={
                                    classNames(classes.link, {
                                      indent: true,
                                      smaller: true,
                                      property: true,
                                      externalLink: !!value.url,
                                    })
                                  }
                                  to={{ pathname: getURL(qualifier) }}
                                  target={!!qualifier.url ? '_blank' : ''}
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
                                        className={
                                          classNames(classes.link, {
                                            property: !!value.ref && value.ref[0] === 'P',
                                            item: !!value.ref && value.ref[0] === 'Q',
                                            externalLink: !!value.url,
                                            smaller: true,
                                          })
                                        }
                                        to={{ pathname: getURL(value) }}
                                        target={!!value.url ? '_blank' : ''}
                                        title={value.url ? value.url : value.units}>
                                        {value.units}
                                      </Link>
                                    </React.Fragment>
                                  ) : value.url || value.ref ? (
                                    <Link
                                      className={
                                        classNames(classes.link, {
                                          indent: false,
                                          smaller: true,
                                          property: !!value.ref && value.ref[0] === 'P',
                                          item: !!value.ref && value.ref[0] === 'Q',
                                          externalLink: !!value.url,
                                        })
                                      }
                                      to={{ pathname: getURL(value) }}
                                      target={!!value.url ? '_blank' : ''}
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
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </Grid>
    )
  }

  const renderGallery = () => {
    return (
      <Grid item xs={12}>
        <ExpansionPanel
          square={true}
          defaultExpanded={true}
          TransitionProps={{ timeout: 0 }}>
          <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" className={classes.heading}>
              Gallery
            </Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails className={classes.paper}>
            <ImageList
              rowHeight={350}
              cols={1.25} gap={15}
              className={classes.imageList}>
              {data.gallery && data.gallery.map((image, index) => (
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
          </ExpansionPanelDetails>
        </ExpansionPanel>
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
          {data.xrefs && data.xrefs.map((property, index) => (
            <Grid container key={index} className={classes.row}>
              <Grid item xs={6}>
                {property.url || property.ref ? (
                  <Link
                    className={
                      classNames(classes.link, {
                        smaller: true,
                        identifier: true,
                        externalLink: !!property.url,
                      })
                    }
                    to={{ pathname: getURL(property) }}
                    target={!!property.url ? '_blank' : ''}
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
                          className={
                            classNames(classes.link, {
                              smaller: true,
                              externalLink: !!value.url,
                            })
                          }
                          to={{ pathname: getURL(value) }}
                          target={!!value.url ? '_blank' : ''}
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
                                className={
                                  classNames(classes.link, {
                                    indent: true,
                                    smaller: true,
                                    externalLink: !!value.url,
                                  })
                                }
                                to={{ pathname: getURL(qualifier) }}
                                target={!!qualifier.url ? '_blank' : ''}
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
                                    className={
                                      classNames(classes.link, {
                                        smaller: true,
                                        externalLink: !!value.url,
                                      })
                                    }
                                    to={{ pathname: getURL(value) }}
                                    target={!!value.url ? '_blank' : ''}
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
      {renderLoading()}
      <Grid item xs={12} style={{ 'opacity': loading ? '0.25' : '1' }}>
        <Grid container spacing={1}>
          {renderBreadcrumbs()}
        </Grid>
      </Grid>
      <Grid item xs={8} style={{ 'opacity': loading ? '0.25' : '1' }}>
        <Grid container spacing={1}>
          {renderDescription()}
          {renderProperties()}
        </Grid>
      </Grid>
      <Grid item xs={4} style={{ 'opacity': loading ? '0.25' : '1' }}>
        <Grid container spacing={1}>
          {renderGallery()}
          {renderIdentifiers()}
        </Grid>
      </Grid>
    </Grid>
  )
}


export default Data
