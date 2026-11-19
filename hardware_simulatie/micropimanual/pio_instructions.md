## What is PIO?

PIO is a tiny extra "mini-processor" inside the Raspberry Pi Pico chip. You give it a very short program, and it runs on its own, next to your normal code. Its job is to handle the I/O pins of the chip very quickly and at exactly the right time.

## The parts

- **State machine:** A helper. The Pico has 8 of them, so up to 8 jobs can run at the same time.
- **Registers (X, Y, ...):** small boxes (implemented in hardware) that each hold one number, like variables in your code.
- **FIFO:** First In, First Out. A short waiting line (a queue) used to pass numbers between your main code and PIO. Your code puts a number in, PIO takes it out, and the other way around.
- **Instructions:** PIO only knows 9 commands (like `jmp`, `mov`, `push`, `pull`). That is very few, but it keeps things fast and simple.

## Things to remember

- A PIO program is tiny: at most 32 instructions.
- Every instruction takes exactly one clock tick, so the timing never changes.

## Instruction set

The PIO has a very small instruction set (the programming language).
<br>

| Instruction | In one sentence |
|---|---|
| `set` | Put a small number (0 to 31) in a register or on a pin |
| `mov` | Copy a value from one place to another |
| `jmp` | Jump to another line, optionally only if a condition is true |
| `pull` | Receive a number from your main code |
| `push` | Send a number to your main code |
| `out` | Take some bits out of OSR |
| `in_` | Add some bits into ISR |
| `nop` | Do nothing (used to waste time) |

## Registers

You cannot use self defined variables in PIO. You only can use a small set of registers.
<br> 
| Register / part | Size | Purpose | Used by |
|---|---|---|---|
| **X** | 32-bit | counters, data | `set`, `mov`, `out`, `in_`, `jmp` |
| **Y** | 32-bit | counters, data | `set`, `mov`, `out`, `in_`, `jmp` |
| **ISR** | 32-bit | Collects data going to the CPU | `in_`, `mov`, `push` |
| **OSR** | 32-bit | Holds data coming from the CPU | `pull`, `out`, `mov` |
| **PC** | 5-bit | Address of the current instruction (0 to 31) | `jmp`, `mov`, `out` |
| **TX FIFO** | 4 words | Queue: CPU to PIO | `pull`<br> (`sm.put()`) |
| **RX FIFO** | 4 words | Queue: PIO to CPU | `push` <br> (`sm.get()`) |
| **IRQ flags** | 8 flags | Signals to the CPU or other state machines | `irq`, `wait` |
| **Pins (GPIO)** | n/a | Read or write chip pins | `set`, `in_`, `out`, `mov`, `wait` |


## Instruction Examples

### `set`: put a value in a register

```python
set(x, 7)       # x = 7
set(y, 0)       # y = 0
```

Works with numbers from 0 to 31 only. The register can have much large numbers but the isntruction only uses 5 bits to store the constant...


### `mov`: copy a value

```python
mov(y, x)            # y = x
mov(y, invert(x))    # y = x with all bits flipped (0 becomes 1, 1 becomes 0)
mov(isr, x)          # isr = x (ready to be pushed to the CPU)
```

Copies a value from one place to another. It can also flip the bits on the way (`invert`).

### `jmp`: jump to another line

```python
label("again")
# ... some instructions ...
jmp("again")         # always jump back to "again"
```

With a condition, it only jumps sometimes:

```python
set(x, 3)
label("loop")
# ... do something ...
jmp(x_dec, "loop")   # if x is not 0: subtract 1 from x and jump to "loop"
```

`x_dec` checks X, subtracts 1, and jumps if X was not 0 before. This runs the loop body 4 times (X = 3, 2, 1, 0).


### `pull`: receive a number from your code

```python
pull()          # wait until the CPU sends a number, put it in OSR
mov(x, osr)     # copy it to x so we can use it
```

In your main code you send the number with `sm.put(5)`. `pull()` waits (blocks) until a number arrives.


### `push`: send a number to your code

```python
mov(isr, x)     # put x in ISR
push()          # send ISR to the CPU
```

In your main code you read it with `sm.get()`. If the queue (FIFO) is full, `push()` waits until your code reads a value.


### `out`: take a few bits from OSR

```python
pull()
out(x, 8)       # take 8 bits (the lowest ones) from OSR and put them in x
```

Useful when you send one big number but want to use it in pieces. Each `out` removes the bits it took, so the next `out` gets the following bits.


### `in_`: collect a few bits into ISR

```python
in_(x, 8)       # shift 8 bits from x into ISR
```

The opposite of `out`: it builds up a number piece by piece in ISR, which you can then `push()` to your code.


### `set` with pins: turn an LED on and off

`set` can also control a pin. This program blinks an LED:

```python
import rp2
from machine import Pin

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    set(pins, 1) [31]    # pin ON, then wait 31 extra ticks
    nop()        [31]    # do nothing for 32 ticks
    nop()        [31]
    nop()        [31]
    set(pins, 0) [31]    # pin OFF, then wait
    nop()        [31]
    nop()        [31]
    nop()        [31]

sm = rp2.StateMachine(0, blink, freq=2000, set_base=Pin(25))
sm.active(1)
```

- `[31]` is a **delay**: the instruction waits 31 extra ticks after running. That slows the PIO down enough for you to see the LED blink.
- `nop()` means "no operation": it does nothing and only uses time.
- `freq=2000` makes the PIO run at 2000 ticks per second, so the LED blinks about 8 times per second.
- `set_base=Pin(25)` tells PIO which pin `set(pins, ...)` controls. Pin 25 is the LED on a regular Pico. On a Pico W the LED is wired differently, so use an LED on another pin instead.

Notice that after `sm.active(1)` your main code does nothing, and the LED keeps blinking by itself. That is the PIO working on its own.


## References

### Complete instruction set table 

| Instruction | Description | Registers | Arguments |
|---|---|---|---|
| `jmp` | Jump, optionally on a condition | X, Y, PC | `label`; condition: `not_x`, `x_dec`, `not_y`, `y_dec`, `x_not_y`, `pin`, `not_osre` |
| `wait` | Stall until a signal matches | none (reads pins/IRQ) | `polarity` (0/1), `gpio(n)`, `pin(n)`, or `irq(n)` |
| `in_` | Shift bits into ISR | ISR | source: `pins`, `x`, `y`, `null`, `isr`, `osr`; `bit_count` (1 to 32) |
| `out` | Shift bits out of OSR | OSR | destination: `pins`, `x`, `y`, `null`, `pindirs`, `pc`, `isr`, `exec`; `bit_count` (1 to 32) |
| `push` | ISR to RX FIFO | ISR | `iffull`, `block` / `noblock` |
| `pull` | TX FIFO to OSR | OSR | `ifempty`, `block` / `noblock` |
| `mov` | Copy a value | X, Y, ISR, OSR, PC, pins, exec | destination, source (`pins`, `x`, `y`, `null`, `status`, `isr`, `osr`), optional `invert(...)` or `reverse(...)` |
| `irq` | Set, clear, or wait on an IRQ flag | none (IRQ flags) | `block`, `clear`, `index`; flag number (0 to 7), optional `rel(n)` |
| `set` | Write a small constant | X, Y, pins, pindirs | destination (`pins`, `x`, `y`, `pindirs`); value (0 to 31) |


HIER NOG MEER UITLEGGEN

Any instruction can also take `.side(value)` and a delay like `[3]`.

### More references

- MicroPython `rp2` docs: https://docs.micropython.org/en/latest/library/rp2.html
- RP2040 datasheet (PIO is Chapter 3): https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf

