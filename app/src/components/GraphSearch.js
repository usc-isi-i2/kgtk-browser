import React, { useEffect, useState } from 'react'
import TextField from '@material-ui/core/TextField'
import Typography from '@material-ui/core/Typography'
import Autocomplete from '@material-ui/lab/Autocomplete'
import ListItemText from '@material-ui/core/ListItemText'
import { makeStyles } from '@material-ui/core/styles'


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


const GraphSearch = ({ nodes, onSelect }) => {

  const classes = useStyles()

  const [open, setOpen] = useState(false)
  const [options, setOptions] = useState(nodes)
  const [inputValue, setInputValue] = useState('')

  useEffect(() => {
    if ( !inputValue || inputValue.length < 2 ) { return }

    const filteredNodes = nodes.filter(node => {
      if ( node.id.indexOf(inputValue) === 0 ) {
        return true
      }
      if ( node.label.indexOf(inputValue) >= 0 ) {
        return true
      }
      return false
    })

    setOptions(filteredNodes)

  }, [inputValue])

  return (
    <Autocomplete
      id="search"
      open={open}
      onOpen={() => {
        setOpen(!!options.length)
      }}
      onClose={() => {
        setOptions(nodes)
        setOpen(false)
      }}
      onChange={(event, value) => onSelect(value)}
      getOptionLabel={option => option.label + ' ' + option.id}
      filterOptions={options => options}
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
            <b>{option.id}</b>
          </Typography>
          <Typography variant="body1">
            {option.label}
          </Typography>
        </ListItemText>
      )}
      options={options}
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
                {params.InputProps.endAdornment}
              </React.Fragment>
            ),
          }}
        />
      )}
    />
  )
}

export default GraphSearch
