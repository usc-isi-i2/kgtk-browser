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
    MuiAppBar: {
      colorPrimary: {
        backgroundColor: '#fefefe',
        color: '#333',
      },
    },
    MuiFormLabel: {
      root: {
        '&.Mui-focused': {
          color: '#111',
        },
      },
    },
    MuiOutlinedInput: {
      root: {
        borderRadius: 0,
        '&:hover': {
          cursor: 'pointer',
        },
        '& fieldset': {
          borderColor: '#333',
        },
        '&:hover fieldset': {
          borderColor: '#111 !important',
        },
        '&.Mui-focused fieldset': {
          borderColor: '#111 !important',
          borderWidth: '1px !important',
        },
        '&.Mui-error fieldset': {
          borderColor: '#f44336 !important',
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
