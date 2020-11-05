import React from 'react';

import { Route, Switch } from 'react-router-dom';

import HomePage from './Pages/HomePage';
import NotFoundPage from './Pages/NotFoundPage';
import HelpPage from './Pages/HelpPage';


const Routes = () => {
  return (
    <Switch>
      <Route exact path="/" component={HomePage} />
      <Route path="/help" component={HelpPage} />
      <Route path="/*" component={NotFoundPage} />
    </Switch>
  );
};

export default Routes;
