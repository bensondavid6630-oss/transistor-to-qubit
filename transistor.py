"""Module A - Transistor simulator (Level 1: Transistor -> classical bit).

Model: NPN BJT used as a low-side switch.

    Vcc --[LED]--[Rc]-- collector
                          |
    Vin --[Rb]-- base ----+  (NPN)
                          |
                        emitter -- GND

* cutoff     : Vin <= Vth                       -> Ic = 0      (LED OFF)
* active     : Ic = beta * Ib < Ic(sat)         -> LED dim
* saturation : beta * Ib >= Ic(sat)             -> LED fully ON, Vce ~ Vce(sat)

The collector voltage is the *output*. It is HIGH when the LED is OFF and LOW
when the LED is ON, i.e. the stage is an inverter (a NOT gate, Level 2).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class BJTSwitch:
    vcc: float = 5.0        # supply voltage [V]
    vth: float = 0.7        # switching threshold (Vbe) [V]
    rb: float = 10_000.0    # base resistor [ohm]
    rc: float = 330.0       # load (collector) resistor [ohm]
    beta: float = 100.0     # current gain
    vf: float = 2.0         # LED forward drop [V]
    vce_sat: float = 0.2    # saturation voltage [V]

    @property
    def i_sat(self) -> float:
        """Maximum collector current set by the load [A]."""
        return (self.vcc - self.vf - self.vce_sat) / self.rc

    def solve(self, vin: float) -> dict:
        """Operating point for a given base-drive voltage ``vin``."""
        ib = (vin - self.vth) / self.rb if vin > self.vth else 0.0
        wanted = self.beta * ib
        ic = min(wanted, self.i_sat)
        if ic <= 0.0:
            region, vout = "cutoff", self.vcc
        else:
            region = "saturation" if wanted >= self.i_sat else "active"
            vout = max(self.vce_sat, self.vcc - self.vf - ic * self.rc)
        return {
            "vin": vin,
            "ib": ib,
            "ic": ic,
            "vout": vout,
            "region": region,
            "led_on": ic > 0.0,
            "led_brightness": ic / self.i_sat,
            "input_bit": int(vin >= self.vth),
            "output_bit": int(vout > self.vcc / 2),
        }

    def sweep(self, vins=None, points: int = 251) -> dict:
        """Sweep Vin from 0..Vcc and return arrays (for plotting)."""
        if vins is None:
            vins = np.linspace(0.0, self.vcc, points)
        rows = [self.solve(float(v)) for v in vins]
        return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def describe(sw: BJTSwitch, vin: float) -> str:
    r = sw.solve(vin)
    return (
        f"Vin={vin:4.2f} V | Ib={r['ib']*1e6:7.1f} uA | Ic={r['ic']*1e3:5.2f} mA | "
        f"Vout={r['vout']:4.2f} V | {r['region']:<10} | LED {'ON ' if r['led_on'] else 'OFF'} | "
        f"in={r['input_bit']} out={r['output_bit']}"
    )


def demo() -> None:
    sw = BJTSwitch()
    print("Level 1 - transistor as a switch (0/1 -> classical bit)")
    for v in (0.0, 0.5, 0.8, 1.0, 1.5, 5.0):
        print(describe(sw, v))
    print("\nEffect of the load resistance on the saturation current:")
    for rc in (100, 330, 1000, 2200):
        print(f"  Rc={rc:5d} ohm -> Ic(sat) = {BJTSwitch(rc=rc).i_sat*1e3:5.2f} mA")
