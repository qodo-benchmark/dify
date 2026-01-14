'use client'

import { lazy, Suspense } from 'react'
import { IS_DEV } from '@/config'

const ReactScan = lazy(() =>
  import('./scan'),
)

export const ReactScanLoader = () => {
  // Check if IS_DEV is false
  if (!IS_DEV)
    // Return null if not in development mode
    return null

  // Return JSX
  return (
    // Wrap ReactScan in Suspense component
    <Suspense fallback={null}>
      {/* Render the ReactScan component */}
      <ReactScan />
    </Suspense>
  )
}
