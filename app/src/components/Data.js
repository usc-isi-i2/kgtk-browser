import React, { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
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
import ArrowRightAltIcon from '@material-ui/icons/ArrowRightAlt'
import CircularProgress from '@material-ui/core/CircularProgress'
import IconButton from '@material-ui/core/IconButton'
import Pagination from '@material-ui/lab/Pagination'
import Tooltip from '@material-ui/core/Tooltip'

import GraphIcon from './GraphIcon'
import ClassGraphViz from './ClassGraphViz'
import useStyles from '../styles/data'
import fetchData from '../utils/fetchData'
import fetchProperty from '../utils/fetchProperty'
import fetchClassGraphData from '../utils/fetchClassGraphData'
import fetchRelatedProperties from '../utils/fetchRelatedProperties'
import fetchRelatedValues from '../utils/fetchRelatedValues'
import classNames from '../utils/classNames'
import formatNumber from '../utils/numbers'


const Data = ({ info }) => {

  const { id } = useParams()

  const classes = useStyles()

  const [data, setData] = useState({})
  const [loading, setLoading] = useState()

  const [propertyData, setPropertyData] = useState({})
  const [relatedProperties, setRelatedProperties] = useState([])
  const [relatedPropertyValues, setRelatedPropertyValues] = useState({})

  const [classGraphData, setClassGraphData] = useState(null)
  const [loadingClassGraphData, setLoadingClassGraphData] = useState(false)

  const [classGraphViz, setClassGraphViz] = useState(false)

  useEffect(() => {

    // reset data when switching between different items/nodes
    setRelatedPropertyValues({})
    setRelatedProperties([])
    setClassGraphData(null)
    setClassGraphViz(false)

    // fetch item data
    setLoading(true)
    fetchData(id).then(data => {
      setLoading(false)
      setData(data)

      // fetch all high cardinality properties
      if ( !!data.properties.length ) {
        data.properties
          .filter(property => property.mode === 'ajax')
          .forEach(property => {
            const numPages = Math.ceil(property.count / 10)
            fetchProperty(id, property.ref).then(data => {
              setPropertyData(prevData => {
                const propertyData = {...prevData}
                propertyData[property.ref] = {
                  count: property.count,
                  ...data,
                  numPages,
                }
                return propertyData
              })
            })
          })
      }
    })
  }, [id])

  useEffect(() => {
    // fetch class graph data
    // (but only if the API supports that)
    if ( !!info && info.hasClassGraphVisualization ) {
      setLoadingClassGraphData(true)
      fetchClassGraphData(id).then(data => {
        setLoadingClassGraphData(false)
        if ( !!Object.keys(data).length ) {

          // add links and neighbors to the node data
          data.links.forEach(link => {
            const a = data.nodes.find(node => node.id === link.source)
            const b = data.nodes.find(node => node.id === link.target)

            if ( !a.neighbors ) {
              a.neighbors = []
            }

            if ( !b.neighbors ) {
              b.neighbors = []
            }

            a.neighbors.push(b)
            b.neighbors.push(a)

            if ( !a.links ) {
              a.links = []
            }

            if ( !b.links ) {
              b.links = []
            }

            a.links.push(link)
            b.links.push(link)
          })

          setClassGraphData(data)
        }
      })
    }
  }, [id, info])

  useEffect(() => {

    // fetch related properties for the `from related items` section
    fetchRelatedProperties(id).then(data => {
      setRelatedProperties(
        data.map(property => ({
          ...property,
          numPages: Math.ceil(property.count / 10)
        }))
      )
    })

  }, [id])

  const handleOnRelatedItemsExpand = useCallback(expanded => {
    if ( !expanded || !relatedProperties.length ) { return }

    // get the first page for all related property values
    relatedProperties.forEach(property => {

      // in `sync` mode use the values that came with the original request
      if ( property.mode === 'sync' ) {
        setRelatedPropertyValues(prevPropertyValues => {
          const propertyValues = {...prevPropertyValues}
          propertyValues[property.ref] = {
            ...propertyValues[property.ref],
            values: property.values,
          }
          return propertyValues
        })
      }

      // in `ajax` mode fetch the first page from the server
      if ( property.mode === 'ajax' ) {
        fetchRelatedValues(id, property.ref).then(data => {
          setRelatedPropertyValues(prevPropertyValues => {
            const propertyValues = {...prevPropertyValues}
            propertyValues[property.ref] = {
              ...propertyValues[property.ref],
              ...data,
            }
            return propertyValues
          })
        })
      }
    })

  }, [id, relatedProperties])

  const handleOnPageChange = useCallback((property, page) => {
    const skip = (page - 1) * 10
    fetchProperty(id, property.ref, skip).then(data => {
      setPropertyData(prevData => {
        const propertyData = {...prevData}
        propertyData[property.ref] = {
          ...propertyData[property.ref],
          ...data,
        }
        return propertyData
      })
    })
  }, [id])

  const handleOnPageChangeRelatedValues = useCallback((property, page) => {
    const skip = (page - 1) * 10
    fetchRelatedValues(id, property.ref, skip).then(data => {
      setRelatedPropertyValues(prevPropertyValues => {
        const propertyValues = {...prevPropertyValues}
        propertyValues[property.ref] = {
          ...propertyValues[property.ref],
          ...data,
        }
        return propertyValues
      })
    })
  }, [id])

  const getURL = item => {

    // if there is an external url, return url that right away
    if ( item.url ) {
      return item.url
    }

    // if there is no external url, link internally to `/kb/item/<node_id>`
    let url = `/${item.ref}`

    // prefix the url with the location of where the app is hosted
    if ( process.env.REACT_APP_FRONTEND_URL ) {
      url = `${process.env.REACT_APP_FRONTEND_URL}${url}`
    }

    return url
  }

  const showClassGraphViz = () => {
    setClassGraphViz(true)
  }

  const hideClassGraphViz = () => {
    setClassGraphViz(false)
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
            { !!classGraphData && (
              <Tooltip arrow placement="right"
                title="View Class Graph Visualization">
                <IconButton
                  color="inherit"
                  title="View Class Graph Visualization"
                  onClick={showClassGraphViz}>
                  <div className={classes.graphIcon}>
                    <GraphIcon />
                  </div>
                </IconButton>
              </Tooltip>
            )}
          </Typography>
          <Typography variant="subtitle1" className={classes.nodeId}>
            { !!data.ref ? `(${data.ref})` : '' }
          </Typography>
          <Typography variant="subtitle1" className={classes.instance}>
              {data.instance_count}
            </Typography>
            <Typography variant="subtitle2" className={classes.instanceStar}>
              {data.instance_count_star}
            </Typography>
          {data.aliases && (
            <Typography variant="subtitle2" className={classes.aliases}>
              {data.aliases.join(' | ')}
            </Typography>
          )}
          <Typography variant="subtitle1" className={classes.description}>
            {data.description}
          </Typography>
          <Typography variant="subtitle2" className={classes.abstract}>
            {data.abstract}
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
                {renderPropertyValues(property)}
              </Grid>
            ))}
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </Grid>
    )
  }

  const renderPropertyValues = property => {
    if ( property.mode === 'ajax' && property.ref in propertyData ) {
      property = propertyData[property.ref]
    }
    return (
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
        {property.mode === 'ajax' && property.numPages > 1 && (
          <Grid container spacing={0} className={classes.pagination}>
            <Grid item xs={12} sm={12} md={12} lg={6} xl={4}>
              <Pagination size="small"
                count={property.numPages}
                onChange={(event, page) =>
                  handleOnPageChange(property, page)} />
            </Grid>
            <Grid item xs={12} sm={12} md={12} lg={6} xl={8}>
              <span className="smaller">
                {formatNumber(property.count)} values
              </span>
            </Grid>
          </Grid>
        )}
      </Grid>
    )
  }

  const renderRelatedItems = () => {
    if ( !relatedProperties.length ) { return }
    return (
      <Grid item xs={12}>
        <ExpansionPanel
          square={true}
          defaultExpanded={false}
          TransitionProps={{ timeout: 0 }}
          onChange={(event, expanded) => handleOnRelatedItemsExpand(expanded)}>
          <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" className={classes.heading}>
              From Related Items
            </Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails className={classes.paper}>
            {relatedProperties && relatedProperties.map((property, index) => (
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
                <Grid item xs={1}>
                  <ArrowRightAltIcon className={classes.arrow} />
                </Grid>
                <Grid item xs={8}>
                  <Grid item xs={12}>
                    {!!relatedPropertyValues[property.ref] && relatedPropertyValues[property.ref].values.map((value, index) => (
                      <Grid container key={index} spacing={0}>
                        <Grid item xs={12}>
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
                    {property.numPages > 1 && (
                      <Grid container spacing={0} className={classes.pagination}>
                        <Grid item xs={12} sm={12} md={12} lg={6} xl={4}>
                          <Pagination size="small"
                            count={property.numPages}
                            onChange={(event, page) =>
                              handleOnPageChangeRelatedValues(property, page)} />
                        </Grid>
                        <Grid item xs={12} sm={12} md={12} lg={6} xl={8}>
                          <span className="smaller">
                            {formatNumber(property.count)} values
                          </span>
                        </Grid>
                      </Grid>
                    )}
                  </Grid>
                </Grid>
              </Grid>
            ))}
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </Grid>
    )
  }

  const renderGallery = () => {
    if ( !!info && !info.hasGallery ) { return }
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
    if ( !!info && !info.hasIdentifiers ) { return }
    return (
      <Grid item xs={12}>
        <ExpansionPanel
          square={true}
          defaultExpanded={true}
          TransitionProps={{ timeout: 0 }}>
          <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" className={classes.heading}>
              Identifiers
            </Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails className={classes.paper}>
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
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </Grid>
    )
  }

  const renderClassGraph = () => {
    if ( !classGraphViz ) { return }
    return (
      <ClassGraphViz
        data={classGraphData}
        loading={loadingClassGraphData}
        hideClassGraphViz={hideClassGraphViz} />
    )
  }

  return (
    <Grid container spacing={1}>
      {renderLoading()}
      {renderClassGraph()}
      <Grid item xs={8} style={{ 'opacity': loading ? '0.25' : '1' }}>
        <Grid container spacing={1}>
          {renderDescription()}
          {renderProperties()}
          {renderRelatedItems()}
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
