import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '../components/ErrorBoundary'

describe('ErrorBoundary', () => {
  it('renderiza children normalmente quando nao ha erro', () => {
    render(
      <ErrorBoundary>
        <p>conteudo ok</p>
      </ErrorBoundary>
    )
    expect(screen.getByText('conteudo ok')).toBeInTheDocument()
  })

  it('renderiza fallback quando componente filho explode', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    function Bomba() {
      throw new Error('teste boundary')
    }

    render(
      <ErrorBoundary>
        <Bomba />
      </ErrorBoundary>
    )

    expect(screen.getByText('Ocorreu um erro inesperado')).toBeInTheDocument()
    expect(screen.getByText('Recarregar')).toBeInTheDocument()

    spy.mockRestore()
  })
})

describe('Smoke: imports criticos', () => {
  it('ErrorBoundary exporta named export', async () => {
    const mod = await import('../components/ErrorBoundary')
    expect(mod.ErrorBoundary).toBeDefined()
  })
})
