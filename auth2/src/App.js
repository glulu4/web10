import logo from './logo.svg';
import useInterface from './interfaces/Interface'
import useMockInterface from './interfaces/MockInterface'
import React from 'react';
import './assets/bulma/css/bulma.min.css';
import ContractPage from './components/Contracts/ContractPage';
import AppStore from './components/AppStore/AppStore';
import CredentialPage from './components/CredentialPage/CredentialPage';
import Settings from './components/Settings/Settings';

function App() {

  const queryParameters = new URLSearchParams(window.location.search)
  const real = queryParameters.get("real")
  const mockI = useMockInterface();
  const realI = useInterface();
  const I = real?realI:mockI;
  window.I = I;
  
  switch (I.mode) {
    case "appstore": return <AppStore I={I} />;
    case "contracts": return <ContractPage I={I} />;
    case "settings": return <Settings I={I} />;
    case "login": return <CredentialPage I={I} />;
    case "signup": return <CredentialPage I={I} />;
    case "forgot": return <CredentialPage I={I} />;
    default: return <AppStore I={I} />;
  }
}

export default App;