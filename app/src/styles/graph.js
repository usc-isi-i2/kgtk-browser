import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  dialog: {
    position: 'absolute',
    top: '5vh',
    left: '1.5vw',
    right: '1.5vw',
    bottom: '3vh',
    '& .MuiDialogContent-root': {
      padding: 0,
    },
  },
  wrapper: {
    overflow: 'hidden',
  },
  title: {
    color: '#333',
    fontWeight: 'bold',
    position: 'absolute',
    top: '1em',
    left: '1em',
  },
  toolbar: {
    fontSize: '1em',
    textAlign: 'center',
    position: 'absolute',
    right: '2vw',
    top: '2vh',
    width: '35vw',
    zIndex: 99999,
  },
  legend: {
    zIndex: 99999,
    padding: '1em',
    background: 'white',
    border: '1px dashed #ccc',
    position: 'absolute',
    top: '5em',
    left: '1.5em',
    pointerEvents: 'none',
    '& h3': {
      marginTop: 0,
    },
    '& b': {
      marginLeft: '3px',
    },
    '& div': {
      marginTop: '2px',
      marginRight: '5px',
      verticalAlign: 'top',
    },
  },
  rootNode: {
    width: '15px',
    height: '15px',
    borderRadius: '50%',
    background: 'limegreen',
    display: 'inline-block',
    verticalAlign: 'middle',
  },
  orangeNode: {
    width: '15px',
    height: '15px',
    borderRadius: '50%',
    background: '#FF7F14',
    display: 'inline-block',
    verticalAlign: 'middle',
  },
  blueNode: {
    width: '15px',
    height: '15px',
    borderRadius: '50%',
    background: '#1477B4',
    display: 'inline-block',
    verticalAlign: 'middle',
  },
  superclass: {
    color: '#BEAED4',
    fontSize: '2em',
    verticalAlign: 'middle',
  },
  subclass: {
    color: '#7DC980',
    fontSize: '2em',
    verticalAlign: 'middle',
  },
  loading: {
    position: 'absolute',
    top: 'calc(50% - 25px)',
    left: 'calc(50% - 25px)',
    color: '#de6720',
    zIndex: 99999,
  },
}))


export default useStyles
