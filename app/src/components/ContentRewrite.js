import React from 'react'
import {
  Route,
  Switch,
  BrowserRouter,
} from 'react-router-dom'

import Content from './Content'


const ContentRewrite = () => (
  <BrowserRouter>
    <Switch>
      <Route exact path='/' component={Content}/>
      <Route exact path='/browser' component={Content}/>
    </Switch>
  </BrowserRouter>
)


export default ContentRewrite
