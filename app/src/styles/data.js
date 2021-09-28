import { makeStyles } from '@material-ui/core/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    paddingTop: theme.spacing(1),
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    paddingBottom: theme.spacing(1),
    borderRadius: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
    color: '#333',
  },
  title: {
    color: '#333',
    fontWeight: 'bold',
  },
  nodeId: {
    fontStyle: 'italic',
  },
  aliases: {
    color: '#999',
  },
  heading: {
    color: '#333',
    fontWeight: 'bold',
  },
  description: {},
  link: {
    display: 'inline-block',
    padding: '0 3px',
    color: '#333',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    transition: '0.2s background ease',
    verticalAlign: 'bottom',
    fontSize: '12px',
    '&:hover': {
      background: '#f3f3f3',
      textDecoration: 'underline',
      color: '#111',
    },
    '&.main': {
      color: '#0077ea',
    },
    '&.indent': {
      marginLeft: theme.spacing(3),
    },
    '&.externalLink': {
      textDecoration: 'underline',
    },
    '&.qualifier': {
      color: '#7059e6',
    },
    '&.property': {
      color: '#0077ea',
    },
    '&.item': {
      color: '#de6720',
    },
  },
  text: {
    display: 'inline-block',
    padding: '0 3px',
    color: '#333',
    fontSize: '12px',
    '&.indent': {
      paddingLeft: theme.spacing(3),
    },
  },
  lang: {
    color: '#777',
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
  imageTitle: {
    color: '#fefefe',
  },
  imageTitleBar: {
    background:
      'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
  },
}))


export default useStyles
