import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  wrapper: {
    overflow: 'hidden',
  },
  toolbar: {
    textAlign: 'right',
    fontSize: '1em',
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
