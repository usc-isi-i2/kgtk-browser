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
    color: '#0c8e7d',
  },
  nodeId: {
    fontStyle: 'italic',
  },
  aliases: {
    color: '#999',
  },
  heading: {
    color: '#0c8e7d',
  },
  description: {},
  link: {
    display: 'inline-block',
    padding: theme.spacing(0),
    textDecoration: 'underline',
    color: '#333',
    cursor: 'pointer',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    width: '100%',
    transition: '0.2s background ease',
    fontSize: '12px',
    '&:hover': {
      background: 'rgba(253, 214, 0, 0.25)',
      color: '#111',
    },
    '&.main': {
      color: '#0077ea',
    },
    '&.indent': {
      paddingLeft: theme.spacing(3),
    },
  },
  text: {
    display: 'inline-block',
    padding: theme.spacing(0),
    color: '#333',
    width: '100%',
  },
  text2: {
    display: 'inline-block',
    padding: theme.spacing(0),
    paddingLeft: theme.spacing(3),
    color: '#333',
    width: '100%',
  },
  text3: {
    display: 'inline-block',
    padding: theme.spacing(0),
    color: '#333',
    width: '100%',
    fontSize: '12px',
  },
  text4: {
    display: 'inline-block',
    padding: theme.spacing(0),
    color: '#333',
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
    color: '#333',
  },
  imageTitleBar: {
    background:
      'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
  },
}))


export default useStyles
