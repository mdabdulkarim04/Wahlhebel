# ******************************************************************************
# -*- coding: latin1 -*-
# File    : N_HaltPhase_kein_bus_knockout.py
# Title   : N_HaltPhase_kein_bus_knockout
# Task    : W�hrend N-Haltphase kein bus knockout
#
# Author  : Devangbhai Patel
# Date    : 14.02.2022
# Copyright 2022 Eissmann Automotive Deutschland GmbH
#
# ******************************************************************************
# ********************************* Version ************************************
# ******************************************************************************
# Rev. | Date       | Name       | Description
# ------------------------------------------------------------------------------
# 1.0  | 14.09.2022 | Devangbhai   | initial



from _automation_wrapper_ import TestEnv
from functions_diag import HexList
from diag_identifier import identifier_dict
import functions_common
from ttk_checks import basic_tests
import functions_gearselection
import time
from time import time as t
import functions_nm
from functions_nm import _checkStatus

from ttk_base.values_base import meta
import os

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
    func_com = functions_common.FunctionsCommon(testenv)
    func_nm = functions_nm.FunctionsNM(testenv)
    diag_ident_KN_CTR = identifier_dict['Knockout_counter']
    diag_ident_KN_TMR = identifier_dict['Knockout_timer']
    diag_ident_KN_TEST_MODE = identifier_dict['Knockout_test_mode']

# Initialize variables ####################################################
    test_variable = hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value
    test_variable.alias = "Waehlhebel_04:WH_Zustand_N_Haltephase_2"

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_XXX")

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] Starte ECU (KL30 an, KL15 an)", ""])
    testenv.startupECU()
    canape_diag = testenv.getCanapeDiagnostic()
    testresult.append([" [.] Tester Present deaktivieren", ""])
    canape_diag.disableTesterPresent()

    testresult.append(["[.] Initialisierungsphase abgeschlossen und Waehlhebelposition D aktiviert", ""])
    descr, verdict = func_gs.changeDrivePosition('D')
    testresult.append(["\xa0" + descr, verdict])
    time.sleep(5)

    # TEST PROCESS ############################################################
    testresult.append(["[#0] Starte Testprozess: %s" % testenv.script_name.split('.py')[0], ""])

    # test step 1
    testresult.append(["[.] Pr�fe WH_Zustand_N_Haltephase_2 = 0", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status=0,
            descr="Pr�fe, dass Wert 0 (inaktiv) ist",
        )
    )

    # test step 2
    testresult.append(["[.] Pr�fe dass KN_Waehlhebel_BusKnockOutTimer und  KN_Waehlhebel_BusKnockOutTimer wert sind zwichen 1 und 62 und speichere diese wert als Ausgangswert", ""])
    start_value_Bus_KN_timer = hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get()
    start_value_ECU_KN_timer = hil.KN_Waehlhebel__KN_Waehlhebel_ECUKnockOutTimer__value.get()

    testresult += [basic_tests.checkRange(start_value_ECU_KN_timer, 1, 62, descr=" 0 < KN_Waehlhebel_ECUKnockOutTimer < 63")]
    testresult += [basic_tests.checkRange(start_value_Bus_KN_timer, 1, 62, descr=" 0 <  KN_Waehlhebel_BusKnockOutTimer < 63")]

    # test step 3
    testresult.append(["[.] Setze SiShift_FlgStrtNeutHldPha = 1,VDSO_Vx3d = 32766 (0 km/h),SIShift_StLghtDrvPosn = 6", ""])
    hil.SiShift_01__SIShift_FlgStrtNeutHldPha__value.set(1)

    descr, verdict = func_gs.setVelocity_kmph(0)
    testresult.append(["\xa0" + descr, verdict])

    descr, verdict = func_gs.changeDrivePosition('N')
    testresult.append(["\xa0" + descr, verdict])

    # test step 4
    testresult.append(["[.] Setze KL15 auf 0 (inactive) und 300ms warten", ""])
    hil.cl15_on__.set(0)
    time.sleep(0.300)

    # test step 5
    testresult.append(["[.] Pr�fe WH_Zustand_N_Haltephase_2 = 1 ", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status=1,
            descr="Pr�fe, dass Wert 1 (aktiv_Timer_laeuft) ist",
        )
    )

    # test step 6
    testresult.append(["[.] 1 min warten", ""])
    time.sleep(60)

    # test step 7
    testresult.append(["[.] Pr�fe dass KN_Waehlhebel_BusKnockOutTimer und  KN_Waehlhebel_BusKnockOutTimer wert sind mit dem gespeicherten Ausgangswert identisch sind.", ""])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_ECUKnockOutTimer__value, start_value_ECU_KN_timer, descr=" Pr�fe dass KN_Waehlhebel_ECUKnockOutTimer == %s" %(start_value_ECU_KN_timer))]
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, start_value_Bus_KN_timer, descr=" Pr�fe dass KN_Waehlhebel_BusKnockOutTimer == %s" %(start_value_Bus_KN_timer))]

    # test step 8
    testresult.append(["[.] Pr�fe WH_Zustand_N_Haltephase_2 = 1 ", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status=1,
            descr="Pr�fe, dass Wert 1 (aktiv_Timer_laeuft) ist",
        )
    )
    # test step 9
    testresult.append(["[.] Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren) Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x4 * (Supress Veto == Active), um BUSKnockOut testen zu k�nnen und warte 2sec", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_1, key_1, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x04]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0 Pr�fe Positive Response: 0x6E 09F3 ist", "INFO"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))
    time.sleep(2)

    # test step 10
    testresult.append(["[.] Warte weitere 3 min", ""])
    time.sleep(60*3)

    # test step 11
    testresult.append(["[.] Pr�fe dass KN_Waehlhebel_BusKnockOutTimer und  KN_Waehlhebel_BusKnockOutTimer wert sind mit dem gespeicherten Ausgangswert identisch sind.", ""])
    testresult += [
        basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_ECUKnockOutTimer__value, start_value_ECU_KN_timer,
                                descr=" Pr�fe dass KN_Waehlhebel_ECUKnockOutTimer == %s" % (start_value_ECU_KN_timer))]
    testresult += [
        basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, start_value_Bus_KN_timer,
                                descr=" Pr�fe dass KN_Waehlhebel_BusKnockOutTimer == %s" % (start_value_Bus_KN_timer))]

    # test step 12
    testresult.append(["[.] Pr�fe WH_Zustand_N_Haltephase_2 = 1 ", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status=1,
            descr="Pr�fe, dass Wert 1 (aktiv_Timer_laeuft) ist",
        )
    )

    # Ttest step 13"
    testresult.append(["[.] Setze SiShift_StLghtDrvPosn = 8 senden, und 300ms warten", ""])
    descr, verdict = func_gs.changeDrivePosition('P')
    time.sleep(0.300)

    # test step 14
    testresult.append(["[.] Pr�fe WH_Zustand_N_Haltephase_2 = 0 ", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Zustand_N_Haltephase_2__value,
            nominal_status=0,
            descr="Pr�fe, dass Wert 0 ist",
        )
    )

    # test step 14
    testresult.append(["[.] Pr�fe dass KN_Waehlhebel_BusKnockOutTimer und  KN_Waehlhebel_BusKnockOutTimer wert sind mit dem gespeicherten Ausgangswert identisch sind.",""])
    testresult += [
        basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_ECUKnockOutTimer__value, start_value_ECU_KN_timer,
                                descr=" Pr�fe dass KN_Waehlhebel_ECUKnockOutTimer == %s" % (start_value_ECU_KN_timer))]
    testresult += [
        basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, start_value_Bus_KN_timer,
                                descr=" Pr�fe dass KN_Waehlhebel_BusKnockOutTimer == %s" % (start_value_Bus_KN_timer))]


    # TEST POST CONDITIONS ####################################################
    testresult.append(["Test Nachbedingungen", "INFO"])
    testresult.append(["ECU ausschalten", "INFO"])
    testenv.shutdownECU()

    # cleanup #################################################################
    hil = None

finally:
    # #########################################################################
    testenv.breakdown()
    del (testenv)

