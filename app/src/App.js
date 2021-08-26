import React from 'react'
import Container from '@material-ui/core/Container'
import CssBaseline from '@material-ui/core/CssBaseline'
import {
  withStyles,
  ThemeProvider,
  createMuiTheme,
  responsiveFontSizes,
} from '@material-ui/core/styles'


import Content from './components/Content'


let theme = createMuiTheme()
theme = responsiveFontSizes(theme)


const styles = theme => ({
  '@global': {
    body: {
      background: 'linear-gradient(150deg, #708090, #002133)',
      backgroundAttachment: 'fixed',
      backgroundSize: '100% 150%',
      padding: theme.spacing(3, 1),
      height: '100vh',
    },
  },
})

const App = () => {

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Content />
    </ThemeProvider>
  )
}


export default withStyles(styles)(App)
