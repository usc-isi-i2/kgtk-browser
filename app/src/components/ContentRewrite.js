import React from 'react'
import { BrowserRouter, Route, Switch} from "react-router-dom";
import Content from './Content'


//	        <Redirect path='/item:id' to='/?id=:id'/>
const ContentRewrite = () => (
	<BrowserRouter>
	    <Switch>
	        <Route exact path='/' component={Content}/>
	        <Route exact path='/browser' component={Content}/>
	    </Switch>
	</BrowserRouter>
)


export default ContentRewrite
