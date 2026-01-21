'use client'

import { lazy, Suspense } from 'react'
import { IS_DEV } from '@/config'

const ReactScan = lazy(() =>
  import('./scan').then(module => ({
    default: module.ReactScan,
  })).catch((error) => {
    console.error('Failed to load React Scan devtools:', error)
    return { default: () => null }
  }),
)

export const ReactScanLoader = () => {
  if (!IS_DEV)
    return null

  return (
    <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}>
      <ReactScan />
    </Suspense>
  )
}
