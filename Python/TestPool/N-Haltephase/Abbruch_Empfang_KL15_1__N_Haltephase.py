#******************************************************************************
# -*- coding: latin-1 -*-
#
# File    : Abbruch_Empfang_KL15_1__N_Haltephase.py
# Title   : N-Haltephase Abbruch Empfang KL15 = 1
# Task    : Test Abbruch der N-Haltephase nach Abbruch Empfang KL15 = 1
#
# Author  : A. Neumann
# Date    : 17.05.2021
# Copyright 2021 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0  | 17.05.2021 | A. Neumann | initial
# 1.1  | 23.06.2021 | Mohammed   | Changing value Strommonitoring (2 mA<I<100mA)
# 1.2  | 02.07.2021 | NeumannA   | Strommonitoring Beschreibung korrigiert
#******************************************************************************
#
# Imports #####################################################################
from _automation_wrapper_ import TestEnv
from ttk_checks import basic_tests
import functions_gearselection
import time

# Instantiate test environment
testenv = TestEnv()

try:
    # #########################################################################
    # Testenv #################################################################
    testenv.setup()
    testresult = testenv.getResults()
    
    # Initialize functions ####################################################
    hil = testenv.getHil()
    daq = testenv.getGammaDAQ()
    func_gs = functions_gearselection.FunctionsGearSelection(testenv, hil)

    # Initialize variables ####################################################
    test_variable = hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value
    test_variable.alias = "Waehlhebel_04:WH_Zustand_N_Haltephase_2"

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_118")
    
    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] Starte ECU (KL30 an, KL15 an)", ""])
    testenv.startupECU()
    testresult.append(["[.] Waehlhebelposition D aktiviert", ""])
    descr, verdict = func_gs.changeDrivePosition('D')
    testresult.append(["\xa0"+descr, verdict])

    # TEST PROCESS ############################################################
    testresult.append(["[-] Starte Testprozess: %s"%testenv.script_name.split('.py')[0], ""])
    testresult.append(["[+] Pr�fe, dass %s zum Teststart wie erwartet gesetzt ist (=0)"%test_variable.alias, ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status = hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status = 0,
            descr = "Pr�fe, dass Wert 0 ist",
            )
        )

    testresult.append(["[.] Pr�fe, dass %s auf 1 wechselt"%test_variable.alias, ""])
    testresult.append(["\xa0Setze SiShift FlgStrtNeutHldPha auf 1 (StartNeutralHoldPhase)", ""])
    hil.SiShift_01__SIShift_FlgStrtNeutHldPha__value.set(1)

    descr, verdict = func_gs.setVelocity_kmph(0)
    testresult.append(["\xa0"+descr, verdict])

    descr, verdict = func_gs.changeDrivePosition('N')
    testresult.append(["\xa0"+descr, verdict])

    testresult.append(["\xa0Setze KL15 auf 0 (inactive)", ""])
    hil.cl15_on__.set(0)
    testresult.append(["[.] Warte 150ms", ""])
    time.sleep(0.15)

    testresult.append(["[+] Pr�fe, dass %s den Wert auf 1 �ndert" % test_variable.alias, ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status=1,
            descr="Pr�fe, dass Wert 1 ist",
        )
    )

    testresult.append(["Schalte Senden von empfangenen Signalen aus (HiL -> ECU)", "INFO"])
    hil.can0_HIL__HIL_TX__enable.set(0)

    testresult.append(["[-] Pr�fe Strommonitoring und Busruhe nach 1 Minute", ""])
    time.sleep(60)
    testresult.append(
        basic_tests.checkRange(
            value = hil.cc_mon__A.get(),
            min_value = 0.002, #2mA
            max_value = 0.100, # 100mA
            descr="Pr�fe, dass Strom zwischen 2mA und 100mA liegt"
            )
    )
    descr, verdict = func_gs.checkBusruhe(daq)
    testresult.append([descr, verdict])

    testresult.append(["Waehlhebel_04__WH_Zustand_N_Haltephase_2: %s"%hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value.get(), "INFO"])

    testresult.append(["[.] Pr�fe, dass nach einer weiteren Minute Busruhe das Aktivieren der KL15 die N-Haltephase abbricht", ""])
    time.sleep(60)
    
    testresult.append(["\xa0Setze KL15 auf 1 (active)", ""])
    hil.cl15_on__.set(1)
    testresult.append(["Schalte Senden von empfangenen Signalen an (HiL -> ECU)", "INFO"])
    hil.can0_HIL__HIL_TX__enable.set(1)
    time.sleep(0.15)

    descr, verdict = basic_tests.checkStatus(
            current_status = hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status = 0,
            descr = "Pr�fe, dass Wert 0 ist",
            )
    testresult.append([descr, verdict])

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[-] Test Nachbedingungen", ""])
    testresult.append(["Shutdown ECU", ""])
    testenv.shutdownECU()
    
    # cleanup
    hil = None

finally:
    # #########################################################################
    testenv.breakdown(ecu_shutdown=False)
