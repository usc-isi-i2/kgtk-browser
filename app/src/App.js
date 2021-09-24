import React from 'react'
import CssBaseline from '@material-ui/core/CssBaseline'
import {
  createTheme,
  ThemeProvider,
  responsiveFontSizes,
} from '@material-ui/core/styles'

import ContentRouter from './components/ContentRouter'


let theme = createTheme({
  overrides: {
    MuiCssBaseline: {
      '@global': {
        html: {
          WebkitFontSmoothing: 'auto',
        },
        body: {
          background: '#fefefe',
          color: '#333',
        },
      },
    },
  },
})
theme = responsiveFontSizes(theme)


const App = () => {

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ContentRouter />
    </ThemeProvider>
  )
}


export default App
