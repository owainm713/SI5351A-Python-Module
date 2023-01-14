# SI5351A-Python-Module
Python module for the Si5351A clock generator

Python 3.x to use with the Si5351A clock generator. Testing done with a Si5351A breakout
 board from Adafuit and a Raspberry Pi3.

created Jan 13, 2023
modified Jan 14, 2023

This uses i2C and requires the smbus python library.

Connections to the Si5351A breakout board from the Pi are as follows:
- Pi 3.3V to Si5351A Vin
- Pi Gnd to Si5351A Gnd
- Pi SCL to Si5351A SCL
- Pi SDA to Si5351A SDI
- SI5351A CLK0 - output
- SI5351A CLK1 - output
- SI5351A CLK2 - output

i2c address - 0x60

The Si5351 datasheet and companion AN619 document are useful for figuring out how to correctly configure the Si5351A for your application.

Current functions include:
set_pll(pll = 'A', synthSettings = (24, 0, 1), intMode = True)
- set the frequency for either PLL A or B
- pll: either 'A' or 'B'
- synthSettings: contains the fractional ratio (a+b/c) used to set the PLL freq in form (a, b, c)
- intMode: True for Integer mode, False for Fractional Mode

set_clk_synth(clk = 0, synthSettings = (1200, 0, 1, 1), intMode = True, divby4 = False)
- set clock frequency
- clk: clock 0-2
- synthSettings: contains the fractional ratio (a+b/c) and R divider value used to set the CLK freq in form (a, b, c, R)
- intMode: True for Integer mode, False for Fractional Mode
- divby4: True, divide by 4 enabled, False, divide by 4 disable

set_clk_control(clk, pwrDown = True, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)
- set various clock attributes
- clk: clock 0-2
- pwrDown: True, clock output driver is powered down, False, clock output driver is powered up
- intMode: True for Integer mode, False for Fractional Mode
- synthSource: either 'A' or 'B' for PLL A or B
- outInv: invert output True/False
- clkSource: valid values are 'XTAL', 'CLK0' & 'SYNTH'
- driveStrength: valid values are 2,4,6,8 for 2,4,6,8 mA 

set_initial_offset(clk, offset = 0)
- set clock offset
- valid value of 0-63 representing offset - see SN619 for calculation

set_spread_spectrum(sscAMP = 0.015, mode = 'CENTER', pllARatio = 24) 
- set spread spectrum attributes
- sscAMP: spread amplitude (for 1% sscAMP = 0.01)
- mode: vaild values 'CENTER' or 'DOWN'
- pllARatio: a+b/c ratio used to set PLL A

set_xtal_capacitance(cap = 10) 
- set internal capacitance for crystal input
- cap: internal capacitance, valid values 6, 8, 10 (pF)

set_clk_disable_state(stateDict = {})
- set the clock output state when disabled
- stateDict: format {clk#:STATE}, valid values are 'LOW', 'HIGH', 'HIGH_IMPEDANCE' and 'NEVER'

disable_all_outputs(pwrDn = True) 
- disables all clock outputs and optionally powers down the clock output drivers
- pwrDn: True also power down the clock output drivers

enable_outputs(clkDict = {})
- enables/disables specified clock outputs
- clkDict: format {clk#:True}, True enable clock, False disable clock.

disable_OEB_pin_all() 
- disables the output enable (OEB) pin for all clock outputs

enable_OEB_pin(clkDict = {})
- enables/disables the output enable (OEB) pin for the specified clock outputs
- clkDict: format {clk#:True}, True OEB pin for clock, False disable OEB pin for clock

fanout_enable(XTAL_FO = False, CLKIN_FO = False, MS_FO = False)
- enables/disables fanout of XTAl, CLKIN and/or Multisynth0/4 directly to the clock outputs

spread_spectrum_enable(enable = True)
- enables/disables spread spectrum output on PLLA and it's associated clock outputs.

pll_reset() - does a soft reset of both PLL A & B

read_status() - returns the value in the interrupt status sticky register

clear_status() - clears the interrupt status sticky register

Notes
Jan 14, 2023 - I have been working with an Si5351A in a 10MSOP package which only has 3 clock outputs (0,1 & 2). To use extend beyond using clock 0-2 the following functions would be need to modified slightly
- set_clk_synth - clocks 3 -7
- set_clk_control - specifically clocks 6 & 7
Other features of the SI5351 I haven't provisioned for are CLKIN (alternate clock input source from the XTAL), and VCXO amongst others


