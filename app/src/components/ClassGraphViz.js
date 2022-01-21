import React, { useCallback, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import Grid from '@material-ui/core/Grid'
import CircularProgress from '@material-ui/core/CircularProgress'
import ArrowRightAltIcon from '@material-ui/icons/ArrowRightAlt'
import AutorenewIcon from '@material-ui/icons/Autorenew'
import IconButton from '@material-ui/core/IconButton'
import Tooltip from '@material-ui/core/Tooltip'
import ForceGraph2D from 'react-force-graph-2d'
import * as d3 from 'd3'

import GraphSearch from './GraphSearch'
import useStyles from '../styles/graph'


const ClassGraphViz = ({ data, loading }) => {

  const fgRef = useRef()

  const { id } = useParams()

  const classes = useStyles()

  const [graphWidth, setGraphWidth] = useState(window.innerWidth)
  const [graphHeight, setGraphHeight] = useState(window.innerHeight)

  window.addEventListener('resize', () => {
    setGraphWidth(window.innerWidth)
    setGraphHeight(window.innerHeight)
  })

  const resetGraph = () => {
    fgRef.current.zoomToFit(500, 75)
    fgRef.current.d3ReheatSimulation()
  }

  const selectNode = useCallback(node => {
    fgRef.current.zoomToFit(500, 75)
    fgRef.current.d3ReheatSimulation()
    fgRef.current.centerAt(node.x, node.y, 1000)
  }, [fgRef])

  const renderGraph = () => {
    if ( !data ) { return }
    return (
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        nodeId={'id'}
        nodeLabel={'tooltip'}
        nodeVal={'size'}
        width={graphWidth}
        height={graphHeight}

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
          return d3.schemeAccent[link.color]
        }}

        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.label
          const fontSize = 12 / globalScale
          ctx.font = `${fontSize}px Sans-Serif`
          const textWidth = ctx.measureText(label).width
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2) // some padding

          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y- 10- bckgDimensions[1] / 2, ...bckgDimensions)

          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'

          ctx.fillStyle = d3.schemeCategory10[node.color]
          if ( node.id === id ) {
            ctx.fillStyle = 'limegreen'
          }

          ctx.fillText(label, node.x, node.y - (node.size + 5))
          ctx.beginPath()
          ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI, false)
          ctx.fill()

          node.__bckgDimensions = bckgDimensions // to re-use in nodePointerAreaPaint
        }}
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
        <p><div className={classes.rootNode} /> Root node</p>
        <p><div className={classes.orangeNode} /> Many Subclasses</p>
        <p><div className={classes.blueNode} /> Few Subclasses</p>
        <p><b>A <ArrowRightAltIcon className={classes.superclass} /> B</b>: B is a superclass of A</p>
        <p><b>A <ArrowRightAltIcon className={classes.subclass} /> B</b>: A is a subclass of B</p>
      </div>
    )
  }

  const renderToolbar = () => {
    if ( !data || !data.nodes ) { return }
    return (
      <Grid container spacing={1} className={classes.toolbar}>
        <Grid item xs={10}>
          <GraphSearch
            nodes={data.nodes}
            onSelect={node => selectNode(node)} />
        </Grid>
        <Grid item xs={2}>
          <Tooltip arrow title="Reset Graph">
            <IconButton
              color="inherit"
              title="Reset Graph"
              onClick={resetGraph}>
              <AutorenewIcon fontSize="large" />
            </IconButton>
          </Tooltip>
        </Grid>
      </Grid>
    )
  }

  return (
    <Grid container spacing={1} className={classes.wrapper}>
      {renderLegend()}
      <Grid item xs={8}>
      </Grid>
      <Grid item xs={4}>
        {renderToolbar()}
      </Grid>
      <Grid item xs={12}>
        {renderLoading()}
        {renderGraph()}
      </Grid>
    </Grid>
  )
}


export default ClassGraphViz
