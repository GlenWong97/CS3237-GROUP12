import React from 'react';
import Button from 'react-bootstrap/Button';
import Layout from '../Templates/Layout';

const HelpPage = () => {
  return (
    <Layout>
      
      <div className="container">

          <a href="/">
            <Button variant="primary" size="lg" className="mt-5 pp-button">
              Back
            </Button>
          </a>
          <div className="container fixed-bg-3 text-center">

          <h1 className="text-center display-4 pb-5 pt-5">Sample Outputs</h1>
  
          <div className="container-fluid text-center vert-center-sm">
            <div className="inner-flex-top">
              <div className="main-30">
                <img className="md-icon" src="/yes.png" alt="yes" />
                <h4 className="text-center pb-5 pt-5">User nods head: Yes</h4>
  
              </div>
              <div className="aside-30 vert-center-m">
                <img className="md-icon" src="/no.png" alt="no" />
                <h4 className="text-center pb-5 pt-5">User shakes head: No</h4>
  
              </div>
            </div>
          </div>
  
        </div>
      </div>

    </Layout>
  )};

export default HelpPage;
