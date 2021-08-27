import React, { useRef, useState } from 'react'
import { alpha, makeStyles } from '@material-ui/core/styles'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import InputBase from '@material-ui/core/InputBase'
import SearchIcon from '@material-ui/icons/Search'
import GitHubIcon from '@material-ui/icons/GitHub'
import CircularProgress from '@material-ui/core/CircularProgress'

import Logo from './Logo'
import search from '../utils/search'


const useStyles = makeStyles(theme => ({
  header: {
    color: '#fefefe',
    marginTop: theme.spacing(3),
  },
  grow: {
    flexGrow: 1,
  },
  appBar: {
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    marginBottom: theme.spacing(3),
    padding: theme.spacing(1),
  },
  menuIcon: {
    width: theme.spacing(8),
    height: theme.spacing(8),
    marginRight: theme.spacing(2),
  },
  title: {
    display: 'none',
    [theme.breakpoints.up('sm')]: {
      display: 'block',
    },
  },
  search: {
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: alpha(theme.palette.common.white, 0.15),
    '&:hover': {
      backgroundColor: alpha(theme.palette.common.white, 0.25),
    },
    marginRight: theme.spacing(2),
    marginLeft: 0,
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(3),
      minWidth: '350px',
      width: 'auto',
    },
  },
  searchIcon: {
    padding: theme.spacing(0, 2),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingIcon: {
    top: theme.spacing(1.2),
    right: theme.spacing(2),
    position: 'absolute',
    pointerEvents: 'none',
    '& .MuiCircularProgress-root': {
      color: '#fefefe',
    },
  },
  inputRoot: {
    color: 'inherit',
  },
  inputInput: {
    padding: theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${theme.spacing(4)}px)`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch',
    },
  },
  sectionDesktop: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'flex',
    },
  },
}))


const Header = () => {

  const classes = useStyles()

  const timeoutID = useRef(null)

  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const handleOnChange = event => {
    const value = event.target.value
    clearTimeout(timeoutID.current)
    timeoutID.current = setTimeout(() => {
      if ( !value ) {
        setResults([])
      } else {
        setLoading(true)
        search(value).then(results => {
          setResults(results)
          setLoading(false)
        })
      }
    }, 500)
  }

  return (
    <div className={classes.grow}>
      <AppBar position="static" className={classes.appBar}>
        <Toolbar>
          <div className={classes.menuIcon}>
            <Logo/>
          </div>
          <Typography className={classes.title} variant="h6" noWrap>
            KGTK Browser
          </Typography>
          <div className={classes.search}>
            <div className={classes.searchIcon}>
              <SearchIcon />
            </div>
            <InputBase
              placeholder="Search…"
              classes={{
                root: classes.inputRoot,
                input: classes.inputInput,
              }}
              inputProps={{ 'aria-label': 'search' }}
              onChange={handleOnChange}
            />
            {loading && (
              <div className={classes.loadingIcon}>
                <CircularProgress size={16} />
              </div>
            )}
          </div>
          <div className={classes.grow} />
          <div className={classes.sectionDesktop}>
            <IconButton
              color="inherit"
              href="https://github.com/usc-isi-i2/kgtk"
              title="Knowledge Graph Toolkit"
              rel="noopener noreferrer nofollow"
              target="_blank">
              <GitHubIcon fontSize="large" />
            </IconButton>
          </div>
        </Toolbar>
      </AppBar>
    </div>
  )
}


export default Header
