// Delayed-unmount closer for exit motion. Entrance can be pure CSS (animation on
// mount); exit cannot: the node is gone the moment state flips unless the unmount
// is delayed. animate(fn) returns an animated closer; one hook per dialog group.
// Usage: panel className += closing ? ' sheet-out' : ' sheet';
//        wrapper className += closing ? ' overlay-out' : '';
//        save and cancel both call the animated closer.
import { useRef, useState } from 'react'

export function useClosable(ms = 160) {
  const [closing, setClosing] = useState(false)
  const busy = useRef(false)
  const animate = (fn) => (...args) => {
    if (busy.current) return
    const done = () => { busy.current = false; setClosing(false); fn?.(...args) }
    // reduced motion: close immediately, never eat the delay
    if (typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches) return done()
    busy.current = true
    setClosing(true)
    setTimeout(done, ms)
  }
  return [closing, animate]
}
