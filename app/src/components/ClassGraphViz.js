import React, { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import Grid from '@material-ui/core/Grid'
import CircularProgress from '@material-ui/core/CircularProgress'
import ForceGraph2D from 'react-force-graph-2d'
import * as d3 from 'd3'

import useStyles from '../styles/data'
import fetchClassGraphData from '../utils/fetchClassGraphData'


const ClassGraphViz = () => {

  const fgRef = useRef()

  const { id } = useParams()

  const classes = useStyles()

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState()

  const [graphWidth, setGraphWidth] = useState(window.innerWidth / 12 * 8)
  const [graphHeight, setGraphHeight] = useState(window.innerHeight / 12 * 8)

  window.addEventListener('resize', () => {
    setGraphWidth(window.innerWidth / 12 * 8)
    setGraphHeight(window.innerHeight / 12 * 8)
  })

  useEffect(() => {
    setLoading(true)
    fetchClassGraphData(id).then(data => {
      setLoading(false)
      setData(data)
    })
  }, [])

  const renderGraph = () => {
    if ( !data ) { return }
    return (
      <ForceGraph2D
        graphData={data}
        nodeId={'id'}
        nodeLabel={'tooltip'}
        nodeVal={'size'}

        width={graphWidth}
        height={graphHeight}

        ref={fgRef}
        onEngineStop={() => fgRef.current.zoomToFit(2500, 75)}
        cooldownTime={5000}

        nodeColor={node => {
          if ( node.color[0] === '#' ) {
            return node.color
          }
          return d3.schemeCategory10[node.color]
        }}

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
          const label = node.label;
          const fontSize = 12/globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y- 10- bckgDimensions[1] / 2, ...bckgDimensions);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';

          ctx.fillStyle = d3.schemeCategory10[node.color];

          ctx.fillText(label, node.x, node.y-10);
          ctx.beginPath(); ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI, false);  ctx.fill();

          node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
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

  return (
    <Grid container spacing={1}>
      {renderLoading()}
      {renderGraph()}
    </Grid>
  )
}


export default ClassGraphViz
