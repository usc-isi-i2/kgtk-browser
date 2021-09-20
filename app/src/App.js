import React from 'react'
import CssBaseline from '@material-ui/core/CssBaseline'
import {
  withStyles,
  createTheme,
  ThemeProvider,
  responsiveFontSizes,
} from '@material-ui/core/styles'


import ContentRouter from './components/ContentRouter'
// import ContentRewrite from './components/ContentRewrite'
// import Content from './components/Content'


let theme = createTheme()
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
      <ContentRouter />
    </ThemeProvider>
  )
}


export default withStyles(styles)(App)
