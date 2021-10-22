import React, { useEffect, useRef, useState }from 'react'
import TextField from '@material-ui/core/TextField'
import Typography from '@material-ui/core/Typography'
import Autocomplete from '@material-ui/lab/Autocomplete'
import ListItemText from '@material-ui/core/ListItemText'
import CircularProgress from '@material-ui/core/CircularProgress'
import { makeStyles } from '@material-ui/core/styles'

import fetchSearchResults from '../utils/fetchSearchResults'


const useStyles = makeStyles(theme => ({
  root: {
    marginRight: theme.spacing(2),
    marginLeft: 0,
    width: '100%',
    maxHeight: '100%',
    padding: theme.spacing(1),
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(3),
      minWidth: '350px',
      width: 'auto',
    },
  },
  paper: {
    backgroundColor: '#fefefe',
    borderRadius: 0,
    '& > div': {
      color: '#333',
    },
    '& > ul': {
      color: '#333',
      padding: 0,
    },
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
}))


const Search = () => {

  const classes = useStyles()

  const timeoutID = useRef(null)

  const [open, setOpen] = useState(false)
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(false)
  const [inputValue, setInputValue] = useState('')

  useEffect(() => {
    if ( !inputValue || inputValue.length < 2 ) { return }

    clearTimeout(timeoutID.current)
    timeoutID.current = setTimeout(() => {
      setLoading(true)
      fetchSearchResults(inputValue).then((results) => {
        setLoading(false)
        setOptions(results)
        setOpen(true)
      })
    }, 500)

  }, [inputValue])

  const onSelect = node => {
    let url = `/browser/${node.ref}`

    // prefix the url with the location of where the app is hosted
    if ( process.env.REACT_APP_FRONTEND_URL ) {
      url = `${process.env.REACT_APP_FRONTEND_URL}${url}`
    }

    window.location = url
  }

  return (
    <Autocomplete
      id="search"
      open={open}
      onOpen={() => {
        setOpen(!!options.length)
      }}
      onClose={() => {
        setOpen(false)
      }}
      onChange={(event, value) => onSelect(value)}
      getOptionSelected={(option, value) => option.description === value.name}
      getOptionLabel={(option) => option.description}
      onInputChange={(event, newInputValue) => {
        setInputValue(newInputValue)
      }}
      classes={{
        root: classes.root,
        paper: classes.paper,
      }}
      renderOption={(option, { selected }) => (
        <ListItemText className={classes.listItem}>
          <Typography variant="body1">
            <b>{option.ref}</b>
          </Typography>
          <Typography variant="body1">
            {option.description}
          </Typography>
        </ListItemText>
      )}
      options={options}
      loading={loading}
      renderInput={(params) => (
        <TextField
          fullWidth
          {...params}
          label="Search..."
          autoCorrect="off"
          autoComplete="off"
          autoCapitalize="off"
          spellCheck="false"
          variant="outlined"
          size="small"
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <React.Fragment>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </React.Fragment>
            ),
          }}
        />
      )}
    />
  )
}

export default Search
