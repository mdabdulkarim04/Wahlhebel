# ******************************************************************************
# -*- coding: latin-1 -*-
#
# File    : ORUnext_VehicleProtectedEnvironment.py
# Title   : ORUnext_VehicleProtectedEnvironment
# Task    : ORUnext in Vehicle Protected Environment
#           
# Author  : M.A. Mushtaq
# Date    : 23.02.2022
# Copyright 2022 iSyst Intelligente Systeme GmbH
#
# ******************************************************************************
# ********************************* Version ************************************
# ******************************************************************************
# Rev. | Date       | Name         | Description
# ------------------------------------------------------------------------------
# 1.0  | 23.02.2022 | M.A. Mushtaq | initial
# 1.1  | 25.04.2022 | Mohammed     | Rework
# 1.2  | 09.05.2022 | Mohammed     | Added Testschritte
# 1.3  | 23.05.2022 | Mohammed     | Aktualisiert  Vorbedingungen
# ******************************************************************************

# ******************************************************************************


from _automation_wrapper_ import TestEnv # @UnresolvedImport
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


    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_297")

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] ECU einschalten", ""])
    testenv.startupECU()
    canape_diag = testenv.getCanapeDiagnostic()

    # TEST PROCESS ############################################################
    testresult.append(["\n Starte Testprozess: {}".format(testenv.script_name.split('.py')[0]), ""])
    # silently go one chapter level up
    testresult.append(["[-0]", ""])

    # test step 1-1.5
    testresult.append(["[.] Setze ung�ltige ORUnext Vorbedingungen", ""])
    testresult.append(["[+] Setze PropulsionSystemActive auf 1 (Aktive)", ""])
    hil.OBD_04__MM_PropulsionSystemActive__value.set(1)
    testresult.append(["[.] Setze OTAMC_D_01 setze auf 2 (VPE_aftersale)", ""])
    hil.OTAMC_D_01__VehicleProtectedEnvironment_D__value.set(2)
    testresult.append(["[.] Setze ORU_CONTROL_A auf  PREPARATION ", ""])
    hil.ORU_Control_A_01__OnlineRemoteUpdateControlA__value.set(2)
    testresult.append(["[.] Setze ORU_CONTROL_D auf RUNNING ", ""])
    hil.ORU_Control_D_01__OnlineRemoteUpdateControlD__value.set(4)
    testresult.append(["[.] Warte 500ms (tMSG_CYCLE) ", ""])
    tMSG_CYCLE = 0.5  # sec
    testresult.append(["[.] Warte 500ms (tMSG_CYCLE) ", ""])
    time.sleep(tMSG_CYCLE)
    testresult.append(["[-0]", ""])

    # test step 2
    testresult.append(["[.] Wechsel in default Session: 0x1001", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('default', read_active_session=False))

    # test step 3
    testresult.append(["[.] Lese aktuelle Diagnose Session aus", ""])
    testresult.extend(canape_diag.checkDiagSession('default'))

    # test step 4
    testresult.append(["[.] Wechsel in Extended Session: 0x1003", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('extended'))

    # test step 5
    testresult.append(["[.] Lese aktuelle Diagnose Session aus", ""])
    testresult.extend(canape_diag.checkDiagSession('extended'))

    # test step 6
    testresult.append(["[.] Wechsel in die Programming Session: 0x1002", ""])
    request_programming = [0x10, 0x02]
    testresult.append(["\xa0Versuchen, in 'programming session' zu wechseln", ""])
    [response, result] = canape_diag.sendDiagRequest(request_programming)
    testresult.append(result)
    testresult.append(["\xa0Auf negative Response �berpr�fen", ""])
    testresult.append(canape_diag.checkNegativeResponse(response, request_programming, 0x22))

    # test step 7-7.10
    testresult.append(["[.] Setze g�ltige ORUnext Vorbedingungen", ""])
    testresult.append(["[+] vbat_cl30__V auf 13V", ""])
    hil.vbat_cl30__V.set(13.0)
    testresult.append(["[.] Setze OTAMC_D_01 setze auf VPE_PRODUCTION", ""])
    hil.OTAMC_D_01__VehicleProtectedEnvironment_D__value.set(1)
    testresult.append(["[.] Setze ORU_CONTROL_A auf IDLE ", ""])
    hil.ORU_Control_A_01__OnlineRemoteUpdateControlA__value.set(0)
    testresult.append(["[.] Setze ORU_CONTROL_D auf  IDLE ", ""])
    hil.ORU_Control_D_01__OnlineRemoteUpdateControlD__value.set(0)
    testresult.append(["[.] Setze VDSO_Vx3d auf 0 km/h (37766)", ""])
    testresult.append(func_gs.setVelocity_kmph(0))
    testresult.append(["[.] Setze Waehlhebelposition P aktiviert", ""])
    testresult.append(func_gs.changeDrivePosition('P'))
    testresult.append(["[.] Setze PropulsionSystemActive auf 0 (NotAktiv) ", ""])
    hil.OBD_04__MM_PropulsionSystemActive__value.set(0)
    testresult.append(["[.] Setze Kein CRC und BZ Fehler ", ""])
    testresult.append(["[.] Setze Kein E2E Timeout ", ""])
    testresult.append(["[.] Warte tMSG_CYCLE:500ms ", ""])
    time.sleep(0.5)
    testresult.append(["[-0]", ""])

    # test step 8
    testresult.append(["[.] Wechsel in default Session: 0x1001", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('default', read_active_session=False))

    # test step 9
    testresult.append(["[.] Lese aktuelle Diagnose Session aus", ""])
    testresult.extend(canape_diag.checkDiagSession('default'))

    # test step 10
    testresult.append(["[.] Wechsel in Extended Session: 0x1003", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('extended'))

    # test step 11
    testresult.append(["[.] Lese aktuelle Diagnose Session aus", ""])
    testresult.extend(canape_diag.checkDiagSession('extended'))

    # test step 12
    testresult.append(["[.] Wechsel in Programming Session: 0x1002", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('programming', ticket_id='FehlerId:EGA-PRM-216'))

    # test step 13
    testresult.append(["[.] Auslesen der Active Diagnostic Session: 0x22F186", ""])
    testresult.extend(canape_diag.checkDiagSession('programming', ticket_id='FehlerId:EGA-PRM-216'))

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[+0]", ""])
    testresult.append(["[-] Test Nachbedingungen", ""])
    testresult.append(["Shutdown ECU", ""])
    testenv.shutdownECU()

    # cleanup
    hil = None

finally:
    # #########################################################################
    testenv.shutdownECU()
    testenv.breakdown()
    # #########################################################################