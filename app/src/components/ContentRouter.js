import React from 'react'
import {
  Route,
  Switch,
  BrowserRouter,
} from 'react-router-dom'

import Content from './Content'
import ItemContent from './ItemContent'


const ContentRouter = () => (
  <BrowserRouter>
    <Switch>
      <Route exact path='/' component={Content} />
      <Route exact path='/browser' component={Content} />
      <Route exact path={process.env.REACT_APP_FRONTEND_URL} component={Content} />
      <Route path='/browser/:id' component={ItemContent} />
      <Route path={`${process.env.REACT_APP_FRONTEND_URL}/:id`} component={ItemContent} />
    </Switch>
  </BrowserRouter>
)


export default ContentRouter
