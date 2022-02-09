import React, { useCallback, useRef } from 'react'
import { useParams } from 'react-router-dom'
import Grid from '@material-ui/core/Grid'
import Dialog from '@material-ui/core/Dialog'
import DialogContent from '@material-ui/core/DialogContent'
import Typography from '@material-ui/core/Typography'
import CircularProgress from '@material-ui/core/CircularProgress'
import ArrowRightAltIcon from '@material-ui/icons/ArrowRightAlt'
import AutorenewIcon from '@material-ui/icons/Autorenew'
import IconButton from '@material-ui/core/IconButton'
import CloseIcon from '@material-ui/icons/Close'
import Tooltip from '@material-ui/core/Tooltip'

import ForceGraph2D from 'react-force-graph-2d'
import { SizeMe } from 'react-sizeme'
import * as d3 from 'd3'

import GraphSearch from './GraphSearch'
import useStyles from '../styles/graph'


const ClassGraphViz = ({ data, loading, hideClassGraphViz, size }) => {

  const fgRef = useRef()

  const { id } = useParams()

  const classes = useStyles()

  const resetGraph = () => {
    fgRef.current.zoomToFit(500, 250)
    fgRef.current.d3ReheatSimulation()
  }

  const selectNode = useCallback(node => {
    fgRef.current.zoomToFit(500, 250)
    fgRef.current.d3ReheatSimulation()
    fgRef.current.centerAt(node.x, node.y, 1000)
  }, [fgRef])

  const renderGraph = () => {
    if ( !data ) { return }
    return (
      <SizeMe
        refreshRate={32}
        monitorWidth={true}
        monitorHeight={true}
        noPlaceholder={true}
        render={({ size }) => (
          <ForceGraph2D
            ref={fgRef}
            graphData={data}
            nodeId={'id'}
            nodeLabel={'tooltip'}
            nodeVal={'size'}

            width={size.width}
            height={size.height}

            nodeColor={node => {
              if ( node.color[0] === '#' ) {
                return node.color
              }
              return d3.schemeCategory10[node.color]
            }}

            onNodeClick={selectNode}

            linkWidth={link => link.width}
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}

            linkColor={link => {
              if ( link.color[0] === "#" ) {
                return link.color
              }
              return d3.schemeSet1[link.color]
            }}

            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.label
              const fontSize = 12 / globalScale
              ctx.font = `${fontSize}px Sans-Serif`
              const textWidth = ctx.measureText(label).width
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2) // some padding

              // only show node labels when there are less than K nodes
              if ( data.nodes.length <= 150 ) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.85)'
                ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - (node.size + 5) - bckgDimensions[1] / 2, ...bckgDimensions)

                ctx.textAlign = 'center'
                ctx.textBaseline = 'middle'

                ctx.fillStyle = d3.schemeCategory10[node.color]
                if ( node.id === id ) {
                  ctx.fillStyle = 'limegreen'
                }

                ctx.fillText(label, node.x, node.y - (node.size + 5))

              } else {
                ctx.fillStyle = d3.schemeCategory10[node.color]
                if ( node.id === id ) {
                  ctx.fillStyle = 'limegreen'
                }
              }

              ctx.beginPath()
              ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI, false)
              ctx.fill()

              node.__bckgDimensions = bckgDimensions // to re-use in nodePointerAreaPaint
            }}
          />
        )}
      />
    )
  }

  const renderLoading = () => {
    if ( !loading ) { return }
    return (
      <CircularProgress
        size={50}
        color="inherit"
        className={classes.loading} />
    )
  }

  const renderLegend = () => {
    return (
      <div className={classes.legend}>
        <h3>Legend</h3>
        <p><div className={classes.rootNode} /> Root Node</p>
        <p><div className={classes.orangeNode} /> Many Subclasses</p>
        <p><div className={classes.blueNode} /> Few Subclasses</p>
        <p><ArrowRightAltIcon className={classes.superclass} /> Superclass Of</p>
        <p><ArrowRightAltIcon className={classes.subclass} /> Subclass Of</p>
      </div>
    )
  }

  const renderToolbar = () => {
    if ( !data || !data.nodes ) { return }
    return (
      <Grid container spacing={1} className={classes.toolbar}>
        <Grid item xs={9}>
          <GraphSearch
            nodes={data.nodes}
            onSelect={node => selectNode(node)} />
        </Grid>
        <Grid item xs={1}>
          <Tooltip arrow title="Reset Graph">
            <IconButton
              color="inherit"
              title="Reset Graph"
              onClick={resetGraph}>
              <AutorenewIcon fontSize="large" />
            </IconButton>
          </Tooltip>
        </Grid>
        <Grid item xs={1}>
        </Grid>
        <Grid item xs={1}>
          <Tooltip arrow title="Close Graph">
            <IconButton
              color="inherit"
              title="Close Graph"
              onClick={hideClassGraphViz}>
              <CloseIcon fontSize="large" />
            </IconButton>
          </Tooltip>
        </Grid>
      </Grid>
    )
  }

  const renderTitle = () => {
    return (
      <Typography variant="h6" className={classes.title}>
        Class Graph Visualization
      </Typography>
    )
  }

  const renderContent = () => {
    return (
      <Grid container spacing={1} className={classes.wrapper}>
        {renderTitle()}
        {renderLegend()}
        {renderToolbar()}
        <Grid item xs={12}>
          {renderLoading()}
          {renderGraph()}
        </Grid>
      </Grid>
    )
  }

  return (
    <Dialog
      open={true}
      maxWidth={'xl'}
      onClose={hideClassGraphViz}
      classes={{paper: classes.dialog}}>
      <DialogContent>
        {renderContent()}
      </DialogContent>
    </Dialog>
  )
}


export default ClassGraphViz
