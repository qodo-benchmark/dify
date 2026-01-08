'use client'

import type { FC, PropsWithChildren } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TanStackDevtoolsLoader } from '@/app/components/devtools/tanstack/loader'

const STALE_TIME = 1000 * 60 * 30 // 30 minutes

export const TanstackQueryInitializer: FC<PropsWithChildren> = (props) => {
  const { children } = props
  const client = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: STALE_TIME,
      },
    },
  })

  return (
    <QueryClientProvider client={client}>
      {children}
      <TanStackDevtoolsLoader />
    </QueryClientProvider>
  )
}
