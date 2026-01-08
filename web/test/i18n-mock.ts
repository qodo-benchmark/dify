import * as React from 'react'
import { vi } from 'vitest'

type TranslationMap = Record<string, string | string[]>

/**
 * Create a t function with optional custom translations
 * Checks translations[key] first, then translations[ns.key], then returns ns.key as fallback
 */
export function createTFunction(translations: TranslationMap, defaultNs?: string) {
  return (key: string, options?: Record<string, unknown>) => {
    // Check if translations[key] is not undefined
    if (translations[key] !== undefined)
      return translations[key]

    // Get namespace from options or use defaultNs
    const ns = (options?.ns as string | undefined) ?? defaultNs
    // Create fullKey by concatenating namespace and key with a dot
    const fullKey = ns ? `${ns}.${key}` : key

    // Check if translations[fullKey] is not undefined
    if (translations[fullKey] !== undefined)
      return translations[fullKey]

    // Create a copy of options object
    const params = { ...options }
    // Delete the ns property from params
    delete params.ns
    // Delete the returnObjects property from params
    delete params.returnObjects
    // Create suffix by stringifying params if there are any keys
    const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''
    // Return the fullKey concatenated with suffix
    return `${fullKey}${suffix}`
  }
}

/**
 * Create useTranslation mock with optional custom translations
 *
 * @example
 * vi.mock('react-i18next', () => createUseTranslationMock({
 *   'operation.confirm': 'Confirm',
 * }))
 */
export function createUseTranslationMock(translations: TranslationMap = {}) {
  return {
    useTranslation: (defaultNs?: string) => ({
      t: createTFunction(translations, defaultNs),
      i18n: {
        language: 'en',
        changeLanguage: vi.fn(),
      },
    }),
  }
}

/**
 * Create Trans component mock with optional custom translations
 */
export function createTransMock(translations: TranslationMap = {}) {
  return {
    Trans: ({ i18nKey, components, children }: {
      i18nKey: string
      components?: Record<string, React.ReactNode>
      children?: React.ReactNode
    }) => {
      const text = translations[i18nKey] ?? i18nKey
      return React.createElement('span', { 'data-i18n-key': i18nKey }, children ?? text)
    },
  }
}

/**
 * Create useMixedTranslation mock
 */
export function createMixedTranslationMock(translations: TranslationMap = {}) {
  return {
    useMixedTranslation: (localeFromOuter?: string) => ({
      t: createTFunction(translations, localeFromOuter),
    }),
  }
}

/**
 * Create useGetLanguage mock
 */
export function createUseGetLanguageMock() {
  return {
    useGetLanguage: () => 'en-US',
  }
}

/**
 * Create complete react-i18next mock (useTranslation + Trans)
 *
 * @example
 * vi.mock('react-i18next', () => createReactI18nextMock({
 *   'modal.title': 'My Modal',
 * }))
 */
export function createReactI18nextMock(translations: TranslationMap = {}) {
  return {
    ...createUseTranslationMock(translations),
    ...createTransMock(translations),
  }
}
