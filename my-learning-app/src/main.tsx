import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import DefaultGameMap from './components/DefaultGameMap'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <DefaultGameMap />
  </StrictMode>,
)
