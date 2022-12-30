import logo from './logo.svg';
import useInterface from './interfaces/Interface'
import useMockInterface from './interfaces/MockInterface'
import React from 'react';
import './assets/bulma/css/bulma.min.css';
import Contracts from './components/Contracts/Contracts';
import AppStore from './components/AppStore/AppStore';

function App() {

  const queryParameters = new URLSearchParams(window.location.search)
  const real = queryParameters.get("real")
  const mockI = useMockInterface();
  const realI = useInterface();
  const I = real?realI:mockI;
  window.I = I;
  
  switch (I.mode) {
    case "app-store": return <AppStore I={I} />;
    case "contracts": return <Contracts I={I} />;
    // case "contract-viewer" : return <ContractViewer I={I} />
    // case "settings": return <Settings I={I} />;
    // case "log-in": return <Login I={I} />;
    // case "sign-up": return <SignUp I={I} />;
    // case "forgot-pass": return <ForgotPass I={I} />;
    default: return <AppStore I={I} />;
  }
}

export default App;