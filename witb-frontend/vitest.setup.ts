import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

window.HTMLElement.prototype.scrollIntoView = vi.fn()
window.HTMLElement.prototype.hasPointerCapture = vi.fn(() => false)
window.HTMLElement.prototype.releasePointerCapture = vi.fn()
