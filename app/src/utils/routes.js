import React from 'react'


const BrowserNodeBreadcrumb = ({ match }) => {
  return (
    <span>{match.params.id}</span>
  )
}


const routes = [
  { path: '/', breadcrumb: 'Home' },
  { path: '/browser', breadcrumb: 'Browser' },
  { path: '/browser/:id', breadcrumb: BrowserNodeBreadcrumb },
]


export default routes
