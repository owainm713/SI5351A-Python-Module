#!/usr/bin/env python3
"""SI5351A, python module for the SI5351A clock generator

created January 8, 2023
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

import smbus
import math

class SI5351A:

    def __init__(self, i2cAddress, xtal = 25):

        self.i2cAddress = i2cAddress
        self.bus = smbus.SMBus(1)
        self.xtal = xtal * 1000000

        return

    def multi_access_write_i2c(self, reg=0x00, regValues = [0x00]):
        """multi_access_write_i2c, function to write to multiple registers at
        once"""
        
        self.bus.write_i2c_block_data(self.i2cAddress, reg, regValues)

        return
    
    def single_access_write_i2c(self, reg=0x00, regValue = 0):
        """single_access_write, function to write to a single 8 bit
        data register"""                  
       
        self.bus.write_byte_data(self.i2cAddress,reg, regValue)
        
        return

    def multi_access_read_i2c(self, reg=0x00, numRead = 1):
        """multi_access_read_i2c, function to read multiple registers at
        once"""

        dataTransfer = self.bus.read_i2c_block_data(self.i2cAddress, reg, numRead)

        return dataTransfer

    def single_access_read_i2c(self, reg=0x00):
        """single_access_read, function to read a single 8 bit data
        register"""                  
       
        dataTransfer=self.bus.read_byte_data(self.i2cAddress,reg)
        
        return dataTransfer

    def get_synth_settings(self, a, b, c):
        """get_synth_settings, function to return the P1, P2, P3
        setttings for a multisynth given the a + b/c values.
        P1, P2, P3 formulas are from the Skyworks AN619 - Manually
        Generating an Si5351 Register Map for 10-MSOP and 20-QFN
        Devices document"""
        
        P1 = 128*a + math.floor(128*(b/c)) - 512
        P2 = 128*b - c*math.floor(128*(b/c))
        P3 = c
        
        return (P1, P2, P3)

    def p_byte_separation(self, P):
        """p_byte_separation, function to separate
        a P value into individual bytes. Values returned
        in a list with the msbyte at 0 and lsbyte at 2"""
        
        indBytes = []
        for i in range(0,20,8):
            indBytes.append((P>>i)&0xFF)
            
        # need to reverse order of data in indBytes for writing to chip
        indBytes.reverse()
        
        return indBytes

    def s_byte_separation(self, P):
        """s_byte_separation, function to separate
        a P value into individual bytes. Values returned
        in a list with the msbyte at 0 and lsbyte at 1"""
        
        indBytes = []
        for i in range(0,16,8):
            indBytes.append((P>>i)&0xFF)
            
        # need to reverse order of data in indBytes for writing to chip
        indBytes.reverse()
        
        return indBytes

    def set_pll(self, pll = 'A', synthSettings = (24, 0, 1), intMode = True):
        """set_pll, function to set the either the A or B
        pll synth"""
        
        pllRegs = {'A':[22, 26], 'B':[23, 34]}
        
        if pll != 'A':
            pll = 'B'
            
        # set PLLA & B source input, XTAL in this case
        # write 0x00 to register 15 - should be default value
        self.single_access_write_i2c(reg=15, regValue=0x00)
            
        # set PLL to fractional or integer  mode
        # bit 6, of either register 22 or 23
        regValue = self.single_access_read_i2c(reg=pllRegs[pll][0])
        regValue = regValue & 0xBF        
        
        if intMode == True:
             # PLL - integer mode
            regValue = regValue + (1<<6)
            
        self.single_access_write_i2c(reg=pllRegs[pll][0], regValue=regValue)
        
        # set PLL sythn P1, P2, P3 registers
        a, b, c = synthSettings[0], synthSettings[1], synthSettings[2]
        pllSettings = self.get_synth_settings(a, b, c)
        p1Bytes = self.p_byte_separation(pllSettings[0])
        p2Bytes = self.p_byte_separation(pllSettings[1])
        p3Bytes = self.p_byte_separation(pllSettings[2])
        regP32 = (p3Bytes[0]<<4) + p2Bytes[0]
        
        pllBytes = p3Bytes[1:] + p1Bytes + [regP32] + p2Bytes[1:]
        self.multi_access_write_i2c(reg=pllRegs[pll][1], regValues = pllBytes)
        
        return

    def set_clk_synth(self, clk = 0, synthSettings = (1200, 0, 1, 1), intMode = True, divby4 = False):
        """set_clk_synth, function to set the either clock 0, 1 or 2
        synth"""
        
        clkRegs = {0:[16, 42], 1:[17, 50], 2:[18, 58]}
        rDivBits = {1:0b000, 2:0b001, 4:0b010, 8:0b011, 16:0b100,
                    32:0b101, 64:0b110, 128:0b111}
            
        # set clk to fractional or integer  mode
        # bit 6, of either register 16, 17 or 18     
        if intMode == True:
            intBit = 0b1 # integer mode      
        else:
            intBit = 0b0 # fractional mode
            
        regValue = self.single_access_read_i2c(reg=clkRegs[clk][0])
        regValue = regValue & 0xBF
        regValue = regValue | (intBit<<6)
        self.single_access_write_i2c(reg=clkRegs[clk][0], regValue=regValue) 
        
        # set clk sythn P1, P2, P3 registers
        a, b, c = synthSettings[0], synthSettings[1], synthSettings[2]
        clkSettings = self.get_synth_settings(a, b, c)
        p1Bytes = self.p_byte_separation(clkSettings[0])
        p2Bytes = self.p_byte_separation(clkSettings[1])
        p3Bytes = self.p_byte_separation(clkSettings[2])
        regP32 = (p3Bytes[0]<<4) + p2Bytes[0]
        
        # add in R divider and divide by 4 info
        p1Bytes[0] = (rDivBits.get(synthSettings[3], 0)<<4) + (divby4<<2) + (divby4<<1) + p1Bytes[0]
        
        clkBytes = p3Bytes[1:] + p1Bytes + [regP32] + p2Bytes[1:]
        self.multi_access_write_i2c(reg=clkRegs[clk][1], regValues = clkBytes)
        
        return

    def set_clk_control(self, clk, pwrDown = True, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2):
        """set_clk_control, function to set the control register for the clk provided"""
        
        clkReg = clk + 16
        synthSources = {'A':0, 'B':1}
        clkSources = {'XTAl':0b00, 'CLKIN':0b01, 'CLK0':0b10, 'SYNTH':0b11}
        driveStrengths = {2:0b00, 4:0b01, 6:0b10, 8:0b11}
        
        controlByte = (pwrDown<<7) + (intMode<<6) + (synthSources.get(synthSource, 0)<<5) + (outInv<<4)
        controlByte = controlByte + (clkSources.get(clkSource, 0b11)<<2) + driveStrengths.get(driveStrength, 0b00)   
        
        self.single_access_write_i2c(reg = clkReg, regValue = controlByte)
        
        return

    def disable_all_outputs(self, pwrDn = True):
        """disable_all_outputs, function to disable and power down all of 
        the clock outputs"""

        # disable outputs
        # write 0xFF to register 3
        self.single_access_write_i2c(reg=3, regValue=0xFF)

        if pwrDn == True:
            # power down all output drivers
            # write 0x80 to registers 16-23
            data = [0x80] * 8
            self.multi_access_write_i2c(reg=16, regValues = data)

        return

    def enable_outputs(self, clkDict = {}):
        """enable_outputs, funcion to enable/disable 1
        or more clock outputs. This sets Register 3"""

        # clkDict format {clk#:True/False}
        # e.g. {0:'True'} - enable CLK0

        regValue = self.single_access_read_i2c(reg = 3)

        
        for k in clkDict:
            if clkDict[k] == True:
                mask = 0xFF & ~(1<<k)
                regValue = regValue & mask
            else:
                mask = 0x00 | (1<<k)
                regValue = regValue | mask        

        #print(hex(regValue))
        self.single_access_write_i2c(reg = 3, regValue = regValue)

        return

    def pll_reset(self):
        """pll_reset, function to do a soft reset of
        both pll A & B. This sets register 177"""

        # Apply PLLA and PLLB soft reset
        # write 0xA0 to register 177
        self.single_access_write_i2c(reg=177, regValue=0xA0)

        return

    def disable_OEB_pin_all(self):
        """disable_OEB_pin_all, function to disable, the
        output enable (OEB) pin for all clock outputs"""

        # write 0XFF to Register 9
        self.single_access_write_i2c(reg=9, regValue=0xFF)

        return

    def enable_OEB_pin(self, clkDict = {}):
        """enable_OEB_pin, function to enable/disable the
        output enable (OEB) pin for 1 or more clock outputs.
        This sets register 9"""

        # clkDict format {clk#:True/Fa;se}
        # e.g. {0:'True'} - enable OEB pin for CLK0

        regValue = self.single_access_read_i2c(reg = 9)

        
        for k in clkDict:
            if clkDict[k] == True:
                mask = 0xFF & ~(1<<k)
                regValue = regValue & mask
            else:
                mask = 0x00 | (1<<k)
                regValue = regValue | mask        

        #print(hex(regValue))
        self.single_access_write_i2c(reg = 9, regValue = regValue)

        return

    def fanout_enable(self, XTAL_FO = False, CLKIN_FO = False, MS_FO = False):
        """fanout_enable, function to enable fanout of XTAl, CLKIN and/or
        Multisynth0/4 directly to the clock outputs. This sets Register 187"""

        fanOutByte = (CLKIN_FO<<7) + (XTAL_FO<<6) + (MS_FO<<4)

        self.single_access_write_i2c(reg = 187, regValue = fanOutByte)

        return

    def set_initial_offset(self, clk, offset = 0):
        """set_initial_offset, function to set an initial offset
        for a clock output."""

        # could improve this function in the future to do the
        # actual calculation

        clkReg = clk + 165
        
        self.single_access_write_i2c(reg = clkReg, regValue = offset)

        return

    def read_status(self):
        """read_status, function to read and return the value in the
        interrupt status sticky register (Register 1)"""

        regValue = self.single_access_read_i2c(reg = 1)

        return regValue

    def clear_status(self):
        """clear_status, function to clear the interrupt status
        sticky register (Register 1)"""

        self.single_access_write_i2c(reg = 1, regValue = 0)

        return

    def spread_spectrum_enable(self, enable = True):
        """spread_spectrum_enable, function to enable/disable spread spectrum
        output on PLLA and it's associated clock outputs. This sets
        bit 7 of Register 149"""

        regValue = self.single_access_read_i2c(reg = 149)

        mask = regValue & 0x7F
        regValue = (enable<<7) | mask

        self.single_access_write_i2c(reg = 149, regValue = regValue)

        return

    def set_spread_spectrum(self,sscAMP = 0.015, mode = 'CENTER', pllARatio = 24):
        """set_spread_spectrum, function to set the spread spectrum parameters.
        This sets registers 149 - 161.  Note PLLA has to be set to fractional mode
        when using spread spectrum feature"""

        # set spread spectrum registers
        xtalF = self.xtal

        # Up/Down Parameter
        # SSUDP[11:0] = Floor(xtalF/4x31500)
        SSUDP = math.floor(xtalF/(4*31500))
        SSUDP_bytes = self.s_byte_separation(SSUDP)

        SSUP = 128*pllARatio*(sscAMP/((1-sscAMP)*SSUDP))
        SSDN = 128*pllARatio*(sscAMP/((1+sscAMP)*SSUDP))

        # Down-spread parameters
        # SSDN_P1[11:0] = Floor(SSDN)
        # SSDN_P2[14:0] = 32,767 * (SSDN-SSDN_P1)
        # SSDN_P3[14:0] = 32,767 = 0x7FFF
        SSDN_P1 = math.floor(SSDN)
        SSDN_P2 = int(32767*(SSDN-SSDN_P1))
        SSDN_P3 = 32767

        SSDN_P1_bytes = self.s_byte_separation(SSDN_P1)
        SSDN_P2_bytes = self.s_byte_separation(SSDN_P2)
        SSDN_P3_bytes = self.s_byte_separation(SSDN_P3)

        if mode == 'CENTER':            
            # Up-spread parameters
            # SSUP_P1[11:0] = Floor(SSUP)
            # SSUP_P2[14:0] = 32,767 * (SSUP-SSUP_P1)
            # SSUP_P3[14:0] = 32,767 = 0x7FFF    
            SSUP_P1 = math.floor(SSUP)
            SSUP_P2 = int(32767*(SSUP-SSUP_P1))
            SSUP_P3 = 32767       
        else:
            # mode = 'DOWN'
            # Up-spread parameters
            # SSUP_P1[11:0] = 0
            # SSUP_P2[14:0] = 0
            # SSUP_P3[14:0] = 1    
            SSUP_P1 = 0
            SSUP_P2 = 0
            SSUP_P3 = 1
            
        SSUP_P1_bytes = self.s_byte_separation(SSUP_P1)
        SSUP_P2_bytes = self.s_byte_separation(SSUP_P2)
        SSUP_P3_bytes = self.s_byte_separation(SSUP_P3)

        reg154 = (SSUDP_bytes[0]<<4) + SSDN_P1_bytes[0]
        reg161 = 0x0F & SSUP_P1_bytes[0]       
        
        # need to add SSC_Mode bit (down vs center spread) to SSDN_P3[14:8] register (register 151)
        # Bit 7: 0 - down spread, 1 - center spread
        if mode == 'CENTER':
            SSDN_P3_bytes[0] = 0x80 + SSDN_P3_bytes[0]            
        else:
            SSDN_P3_bytes[0] = 0x7F & SSDN_P3_bytes[0]       
        
        SS_bytes = SSDN_P2_bytes + SSDN_P3_bytes + SSDN_P1_bytes[1:] + [reg154]
        SS_bytes = SS_bytes + SSUDP_bytes[1:] + SSUP_P2_bytes + SSUP_P3_bytes + SSUP_P1_bytes[1:] + [reg161]

        self.multi_access_write_i2c(reg=149, regValues = SS_bytes)

        return

    def set_xtal_capacitance(self, cap = 10):
        """set_xtal_capacitance, function to set the internal load capacitance
        for the crystal. Valid values are 6,8 and 10pF. This sets Register 183"""

        capValues = {6:0b01, 8:0b10, 10:0b11}
        regValue = (capValues[cap]<<6) + 0b010010

        self.single_access_write_i2c(reg = 183, regValue = regValue)

        return

    def set_clk_disable_state(self, stateDict = {}):
        """set_clk_disable_state, function to set the clock output
        state when it is disabled. Valid values are LOW, HIGH, HIGH_IMPEDANCE
        and NEVER. This sets Registers 24 and 25"""

        # stateDict format {clk#:STATE}
        # e.g. {0:'HIGH_IMPEDANCE', 2:'LOW'}

        stateValues = {'LOW':0b00, 'HIGH':0b01, 'HIGH_IMPEDANCE':0b10, 'NEVER':0b11}
        regPositions = [0, 2, 4, 6, 0, 2, 4, 6] # bit offsets for the 8 clocks

        regValue1 = self.single_access_read_i2c(reg = 24)
        regValue2 = self.single_access_read_i2c(reg = 25)

        for k in stateDict:
            if k < 4:
                # clocks 0 to 3
                mask = regValue1 & ~(0b11<<regPositions[k])
                if stateDict[k] == 'LOW':
                    regValue1 = mask
                else:
                    regValue1 =  regValue1 | (stateValues.get(stateDict[k], 0b00)<<regPositions[k])
            else:
                # clocks 4 to 7
                mask = regValue2 & ~(0b11<<regPositions[k])
                if stateDict[k] == 'LOW':
                    regValue2 = mask
                else:
                    regValue2 =  regValue2 | (stateValues.get(stateDict[k], 0b00)<<regPositions[k])
        
        self.multi_access_write_i2c(reg=24, regValues = [regValue1, regValue2])

        return



if __name__ == "__main__":

    clockGen = SI5351A(0x60)

    # disable outputs
    clockGen.disable_all_outputs()

    # disable OEB pin for all clocks
    clockGen.disable_OEB_pin_all()

    # set PLLA to 600MHz - Integer Mode
    clockGen.set_pll('A', (24, 0, 1), intMode = True)

    # set CLK0 to 125kHz - Integer mode
    # set CLK0 control register, register 16 - powered up,
    # integer mode, PLLA, output not inverted, drive strength 2mA
    clockGen.set_clk_control(0, pwrDown = False, intMode = True, synthSource = 'A', outInv = False, clkSource = 'SYNTH', driveStrength = 2)    
    
    # set CLK0 syth 
    clockGen.set_clk_synth(0, synthSettings = (1200, 0, 1, 4), intMode = True, divby4 = False)

    # PLL reset
    clockGen.pll_reset()

    # enable CLK0 output
    clockGen.enable_outputs({0:False})

    # enable/disable fanouts
    clockGen.fanout_enable(XTAL_FO = False, CLKIN_FO = False, MS_FO = False)

    # set spread spectrum parameters
    clockGen.set_spread_spectrum(sscAMP = 0.015, mode = 'CENTER', pllARatio = 24)

    # enable/disable spread spectrum
    clockGen.spread_spectrum_enable(False)

    
    

    


        

    

        
