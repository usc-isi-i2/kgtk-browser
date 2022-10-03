import React from 'react'
import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import CircularProgress from '@material-ui/core/CircularProgress'
import { withStyles } from '@material-ui/core/styles'

import Input from './Input'
import WikidataLogo from './WikidataLogo'

import fetchSearchResults from '../utils/fetchSearchResults'
import fetchESSearchResults from '../utils/fetchESSearchResults'


const styles = theme => ({
  paper: {
    marginTop: theme.spacing(3),
    paddingTop: theme.spacing(3),
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(4),
    paddingBottom: theme.spacing(5),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    position: 'relative',
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(3),
  },
  resultWrapper: {
    position: 'relative',
    marginTop: theme.spacing(3),
  },
  index: {
    color: '#333',
    position: 'absolute',
    top: theme.spacing(1),
    left: theme.spacing(1),
  },
  result: {
    color: '#333',
    width: '97%',
    display: 'inline-block',
    padding: theme.spacing(1),
    marginLeft: theme.spacing(5),
    transition: '0.2s background ease',
    '&:hover': {
      color: '#111',
      background: 'rgba(253, 214, 0, 0.25)',
      textDecoration: 'none',
    },
  },
  label: {
    color: '#0077ea',
    fontSize: '1.5rem',
    lineHeight: '2rem',
    textDecoration: 'underline',
  },
  description: {
    color: '#333',
    textDecoration: 'none',
  },
  settingsToggle: {
    position: 'relative',
    cursor: 'pointer',
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
    color: '#333',
    width: '100%',
    userSelect: 'none',
    '@media (min-width:600px)': {
      marginTop: theme.spacing(3),
    },
  },
  settingsLabel: {
    color: '#333',
    userSelect: 'none',
    '&.Mui-focused': {
      color: '#333',
    },
  },
  settingsRadioGroup: {
    color: '#333',
    userSelect: 'none',
  },
  languageSetting: {
    color: '#333',
    cursor: 'pointer',
    fontWeight: 'bold',
    fontSize: theme.spacing(2),
  },
  alignedIcon: {
    verticalAlign: 'bottom',
  },
  listItem: {
    cursor: 'pointer',
    '& .MuiTypography-body1': {
      maxWidth: '500px',
      overflow: 'hidden',
      whiteSpace: 'nowrap',
      textOverflow: 'ellipsis',
    },
  },
  loading: {
    position: 'absolute',
    top: 'calc(50% - 25px)',
    left: 'calc(50% - 25px)',
    color: '#de6720',
    zIndex: 99999,
  },
})


class Search extends React.Component {

  constructor (props) {
    super(props)

    this.state = {
      query: '',
      results: [],
      loading: false,
    }
  }

  handleOnChange(query) {
    this.setState({ loading: true, query }, () => {
      if ( !query ) {
        this.setState({ loading: false, results: []})
      } else {
        clearTimeout(this.timeoutID)
        this.timeoutID = setTimeout(() => {
          this.submitQuery()
        }, 500)
      }
    })
  }

  submitQuery() {
    const { query } = this.state

    if ( process.env.REACT_APP_USE_KGTK_KYPHER_BACKEND === '1' ) {
      fetchSearchResults(query).then((results) => {
        this.setState({
          results: results,
          loading: false,
        })
      })
    } else {
      fetchESSearchResults(query).then((results) => {
        this.setState({
          results: results,
          loading: false,
        })
      })
    }
  }

  submit(event) {
    event.preventDefault()
    this.submitQuery()
  }

  getBrowsertUrl(node) {
    let url = `/${node.ref}`

    // prefix the url with the location of where the app is hosted
    if ( process.env.REACT_APP_FRONTEND_URL ) {
      url = `${process.env.REACT_APP_FRONTEND_URL}${url}`
    }

    return url
  }

  getWikidataUrl(result) {
    // check if result is a qnode or a property
    if ( result.qnode[0] === 'Q' ) {
      return `https://www.wikidata.org/wiki/${result.qnode}`
    } else {
      return `https://www.wikidata.org/wiki/Property:${result.qnode}`
    }
  }

  renderResults() {
    const { classes } = this.props
    const { loading, query, results } = this.state
    if ( !loading && !!query && !results.length ) {
      return (
        <Grid item xs={12} className={classes.resultWrapper}>
          <Typography
            component="h5"
            variant="h5"
            className={classes.index}>
            There are no results for this query
          </Typography>
        </Grid>
      )
    }
    return results.map((result, i) => (
      <Grid item xs={12} key={i} className={classes.resultWrapper}>
        <Typography
          component="h5"
          variant="h5"
          className={classes.index}>
          {i + 1}.
        </Typography>
        <div className={classes.result}>
          <Typography
            variant="a"
            component="a"
            className={classes.label}
            href={this.getBrowsertUrl(result)}>
            {result.description} ({result.ref})
          </Typography>
          { !!result.qnode ? (
          <Typography
            variant="a"
            component="a"
            target="_blank"
            className={classes.label}
            href={this.getWikidataUrl(result)}>
            <WikidataLogo />
          </Typography>
          ) : null }
          <Typography
            component="p"
            variant="body1"
            className={classes.description}>
            <b>Description:</b> {!!result.description ? result.description : 'No Description'}
          </Typography>
          { !!result.alias && result.alias.length ? (
            <Typography
              component="p"
              variant="body1"
              className={classes.description}>
              <b>Alias:</b> {result.alias.join(', ')}
            </Typography>
          ) : null }
          { !!result.data_type ? (
            <Typography
              component="p"
              variant="body1"
              className={classes.description}>
              <b>Data type:</b> {result.data_type}
            </Typography>
          ) : null }
        </div>
      </Grid>
    ))
  }

  renderSearchBar() {
    return (
      <Grid item xs={12}>
        <Input autoFocus={ true } label={'Search'}
          onChange={ this.handleOnChange.bind(this) }/>
      </Grid>
    )
  }

  renderLoading() {
    if ( !this.state.loading ) { return }
    const { classes } = this.props
    return (
      <CircularProgress
        size={50}
        color="inherit"
        className={classes.loading} />
    )
  }

  render() {
    const { classes } = this.props
    return (
      <form className={classes.form} noValidate
        onSubmit={this.submit.bind(this)}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper component="div" className={classes.paper} square>
              <Grid container spacing={3}>
                {this.renderSearchBar()}
              </Grid>
            </Paper>
            {this.renderResults()}
            {this.renderLoading()}
          </Grid>
        </Grid>
      </form>
    )
  }
}


export default withStyles(styles)(Search)
