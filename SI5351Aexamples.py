#!/usr/bin/env python3
"""SI5351Aexamples, example file with different examples of how to
use the SI5351A python library

created January 10, 2023
last modified January 14, 2023"""

"""
Copyright 2023 Owain Martin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# example 1: setting CLK0 to 1.5MHz - Integer mode
# example 2: setting CLK0 to 125kHz - Integer mode
# example 3: pass through CLK0 (500kHz) to CLK1
# example 4: setting CLK0 to 1.5MHz, setting CLK1 to 1MHz
# example 5: setting CLK2 to 556.575kHz - Fractional mode
# example 6: setting CLK0 to 1.5MHZ - Fractional mode with SS enabled at 1.5% center spread
# example 7: set both CLK0 & CLK1 to 1.5MHz,add 27ns offset to CLK1
# example 9: disable all clock outputs and power down output drivers

import SI5351A

example = 9

clockGen = SI5351A.SI5351A(0x60)

# disable outputs
clockGen.disable_all_outputs()

# disable OEB pin for all clocks
clockGen.disable_OEB_pin_all()

if example == 1:
    # set CLK0 to 1.5MHz - Integer mode

    # set PLLA to 600MHz - Integer Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = True)

    # set CLK0 to 1.5MHz - Integer mode
    # set CLK0 control register, register 16 - powered up,
    # integer mode, PLLA, output not inverted, drive strength 2mA
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)    
    
    # set CLK0 syth 
    clockGen.set_clk_synth(0, synthSettings = (400, 0, 1, 1), intMode = True, divby4 = False)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 output
    clockGen.enable_outputs({0:True})

elif example == 2:
    # set CLK0 to 125kHz - Integer mode

    # set PLLA to 600MHz - Integer Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = True)

    # set CLK0 to 125kHz - Integer mode    
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)     
    clockGen.set_clk_synth(0, synthSettings = (1200, 0, 1, 4), intMode = True, divby4 = False)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 output
    clockGen.enable_outputs({0:True})

elif example == 3:
    # pass through CLK0 (500kHz) to CLK1

    # set PLLA to 600MHz - Integer Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = True)

    # set CLK0 to 500kHz - Integer mode    
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)
    clockGen.set_clk_synth(0, synthSettings = (1200, 0, 1, 0), intMode = True, divby4 = False)

    # set CLK1 control register, register 17 - powered up,
    # integer mode, PLLA, output not inverted, clock 0, drive strength 2mA
    clockGen.set_clk_control(1, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'CLK0', driveStrength = 2)
    
    # enable multisynth fanout
    clockGen.fanout_enable(MS_FO = True)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 & CLK1 output
    clockGen.enable_outputs({0:True, 1:True})

elif example == 4:
    #setting CLK0 to 1.5MHz, setting CLK1 to 1MHz

    # set PLLA to 600MHz - Integer Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = True)

    # set CLK0 to 1.5MHz - Integer mode    
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)    
    clockGen.set_clk_synth(0, synthSettings = (400, 0, 1, 1), intMode = True, divby4 = False)

    # set CLK1 to 1.5MHz - Integer mode    
    clockGen.set_clk_control(1, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)     
    clockGen.set_clk_synth(1, synthSettings = (600, 0, 1, 1), intMode = True, divby4 = False)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 & CLK1 output
    clockGen.enable_outputs({0:True, 1:True})

elif example == 5:
    #setting CLK2 to 556.575kHz - Fractional mode

    # set PLLB to 612.5MHz - Fractional Mode
    clockGen.set_pll('B', (24, 1, 2), intMode = False)

    # set CLK2 to 556.575kHz - Fractional mode
    # set CLK2 control register, register 18 - powered up,
    # fractional mode, PLLA, output not inverted, drive strength 2mA
    clockGen.set_clk_control(2, pwrDown = False, intMode = False, synthSource = 'B', outInv = False, clkSource = 'SYNTH', driveStrength = 2)    
    clockGen.set_clk_synth(2, synthSettings = (1100, 13, 27, 1), intMode = False, divby4 = False)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK2 output
    clockGen.enable_outputs({2:True})

elif example == 6:
    # setting CLK0 to 1.5MZ - Fractional mode with SS enabled at 1.5% center spread    

    # set PLLA to 600MHz - Fractional Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = False)

    # set CLK0 to 1.5MHz - Integer Mode mode    
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)    
    clockGen.set_clk_synth(0, synthSettings = (400, 0, 1, 1), intMode = True, divby4 = False)

    # set spread spectrum parameters
    clockGen.set_spread_spectrum(sscAMP = 0.015, mode = 'CENTER', pllARatio = 24)

    # enable/disable spread spectrum
    clockGen.spread_spectrum_enable(True)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 & CLK1 output
    clockGen.enable_outputs({0:True})

elif example == 7:
    # set both CLK0 & CLK1 to 1.5MHz,add 27ns offset to CLK1

    # set PLLA to 600MHz - Integer Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = True)

    # set CLK0 to 1.5MHz - Integer mode    
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)    
    clockGen.set_clk_synth(0, synthSettings = (400, 0, 1, 1), intMode = True, divby4 = False)

    # set CLK1 to 1.5MHz - Fractional mode    
    clockGen.set_clk_control(1, pwrDown = False, intMode = False, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)     
    clockGen.set_clk_synth(1, synthSettings = (400, 0, 1, 1), intMode = False, divby4 = False)

    # add 27ns offset to CLK1
    clockGen.set_initial_offset(1, 63)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 & CLK1 output
    clockGen.enable_outputs({0:True, 1:True})

    
elif example == 9:
    # disable all clock outputs
    clockGen.disable_all_outputs()

    # disable spread spectrum
    clockGen.spread_spectrum_enable(False)

    # clear CLK1 offset
    clockGen.set_initial_offset(1, 0)
    

    
