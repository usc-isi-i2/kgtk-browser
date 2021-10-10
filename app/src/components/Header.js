import React from 'react'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import GitHubIcon from '@material-ui/icons/GitHub'

import Logo from './Logo'
import Search from './Search'
import useStyles from '../styles/header'


const Header = ({ info }) => {

  const classes = useStyles()

  return (
    <div className={classes.grow}>
      <AppBar position="static" className={classes.appBar}>
        <Toolbar>
          <div className={classes.logo}>
            <Logo/>
          </div>
          <Typography className={classes.title} variant="h6" noWrap>
            KGTK Browser{info ? `: ${info.graph_id}` : ''}
          </Typography>
          <div className={classes.grow} />
            <Search />
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
