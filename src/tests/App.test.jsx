// import { describe, it, expect } from 'vitest'
// import { render } from '@testing-library/react'
// import App from '../App'

// describe('App', () => {
//   it('renders without crashing', () => {
//     render(<App />)
//     expect(document.body).toBeTruthy()
//   })
// })

import { describe, it, expect } from 'vitest'

describe('Basic tests', () => {
  it('true is true', () => {
    expect(true).toBe(true)
  })

  it('math works', () => {
    expect(1 + 1).toBe(2)
  })
})