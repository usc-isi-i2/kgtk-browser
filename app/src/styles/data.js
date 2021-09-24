import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    paddingTop: theme.spacing(1),
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    paddingBottom: theme.spacing(1),
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    borderRadius: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
    color: '#fefefe',
  },
  link: {
    display: 'inline-block',
    padding: theme.spacing(0),
    textDecoration: 'underline',
    color: '#fefefe',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
    },
  },
  link2: {
    display: 'inline-block',
    paddingLeft: theme.spacing(3),
    color: '#fefefe',
    textDecoration: 'underline',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
    },
  },
  link3: {
    display: 'inline-block',
    padding: theme.spacing(0),
    textDecoration: 'underline',
    color: '#fefefe',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
    transition: '0.2s background ease',
    fontSize: 10,
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
    },
  },
  link4: {
    display: 'inline-block',
    padding: theme.spacing(0),
    textDecoration: 'underline',
    color: '#fefefe',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    verticalAlign: 'bottom',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
    },
  },
  text: {
    display: 'inline-block',
    padding: theme.spacing(0),
    color: '#fefefe',
    width: '100%',
  },
  text2: {
    display: 'inline-block',
    padding: theme.spacing(0),
    paddingLeft: theme.spacing(3),
    color: '#fefefe',
    width: '100%',
  },
  text3: {
    display: 'inline-block',
    padding: theme.spacing(0),
    color: '#fefefe',
    width: '100%',
    fontSize: 10,
  },
  text4: {
    display: 'inline-block',
    padding: theme.spacing(0),
    color: '#fefefe',
  },
  lang: {
    color: '#d4d4d4',
    marginLeft: theme.spacing(1),
  },
  row: {
    paddingTop: theme.spacing(0),
    paddingBottom: theme.spacing(0),
    borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
  },
  imageList: {
    flexWrap: 'nowrap',
    // Promote the list into his own layer on Chrome.
    // This cost memory but helps keeping high FPS.
    transform: 'translateZ(0)',
  },
  imageItem: {
    width: '50%',
    height: '300px',
  },
  title: {
    color: '#fefefe',
  },
  titleBar: {
    background:
      'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
  },
  inlineFlex: {
    flex: 1,
    flexDirection: 'row',
  },
}))


export default useStyles
