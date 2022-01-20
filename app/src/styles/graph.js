import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  wrapper: {
    overflow: 'hidden',
  },
  toolbar: {
    fontSize: '1em',
    textAlign: 'center',
  },
  legend: {
    zIndex: 99999,
    padding: '1em 2em',
    background: 'white',
    border: '1px dashed #ccc',
    position: 'absolute',
    pointerEvents: 'none',
    '& b, div': {
      marginLeft: '5px',
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
