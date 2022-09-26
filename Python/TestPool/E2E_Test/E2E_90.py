# ******************************************************************************
# -*- coding: latin1 -*-
# File    : E2E_90.py
# Title   : ORU_Control_D_CRC_BZ_Error
# Task    : Gleichzeigige Fehlerbeaufschlagung mit CRC-Fehler und BZ-Fehler nach 15 empfangenen S-PDUs
#
# Author  : Devangbhai Patel
# Date    : 31.07.2022
# Copyright 2022 Eissmann Automotive Deutschland GmbH
#
# ******************************************************************************
# ********************************* Version ************************************
# ******************************************************************************
# Rev. | Date       | Name       | Description
# ------------------------------------------------------------------------------
# 1.0  | 31.07.2022 | Devangbhai   | initial
# 1.1  | 16.08.2022 | Devangbhai   | Added 2.5 wait time insted of 1.5 in test step 1.1. Added extra wait time and clearing of dtc in test step 7
# 1.2  | 19.08.2022 | Devangbhai   | Added correct Precondition
# 1.3  | 22.08.2022 | Devangbhai   | Reworked according to new specification



from _automation_wrapper_ import TestEnv
from functions_diag import HexList
from diag_identifier import identifier_dict
import functions_common
from ttk_checks import basic_tests
import functions_gearselection
import time
from time import time as t
import functions_nm
from ttk_base.values_base import meta
import os


def checkProgrammingPrecondition(exp_content):
    """ Checks the programming precondition
    Parameters:
        exp_content - expected content as list of bytes
    Returns:
        None
    """
    # test step
    request = [0x31, 0x01] + test_data['identifier']
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Auf positive Response �berpr�fen", ""])
    testresult.append(canape_diag.checkPositiveResponse(response, request, 4))

    # test step
    testresult.append(["\xa0 Pr�fe Inhalt der Response", ""])
    if exp_content:
        testresult.append(basic_tests.checkStatus(meta(len(response[4:]),
                                                       alias="L�nge des Inhalts"),
                                                  len(exp_content),
                                                  descr="{} Element".format(len(exp_content))))
        if len(response[4:]) == len(exp_content):
            testresult.append(basic_tests.compare(meta(response[4:],
                                                       alias="Inhalt"),
                                                  "==",
                                                  meta(exp_content,
                                                       alias="Erwarteter Inhalt"),
                                                  descr="Inhalt der Response"))
        else:
            testresult.append(['Inhalt der Response kann nicht verglichen werden.', 'FAILED'])
    else:
        testresult.append(basic_tests.checkStatus(meta(len(response[4:]),
                                                       alias="L�nge des Inhalts"),
                                                  0,
                                                  descr="Kein Inhalt - Liste leer"))


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
    test_data = identifier_dict['Check Programming Preconditions']
    exp_wrong_prec = [0xA7]

    aktiv_dtc = [(0xE00108, 0x27)]
    passiv_dtc = [(0xE00108, 0x26)]

    aktiv_dtc_bz = [(0xE0010B, 0x27)]
    passiv_dtc_bz = [(0xE0010B, 0x26)]

    # set Testcase ID #########################################################
    testresult.setTestcaseId("E2E_90")

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] Starte ECU (KL30 an, KL15 an)", ""])

    hil.OTAMC_D_01__VehicleProtectedEnvironment_D__value.set(0)
    testresult.append(["[.] Setze OTAMC_D_01 VehicleProtectedEnvironment auf 0", ""])
    hil.OTAMC_D_01__VehicleProtectedEnvironment_D__value.set(0)

    testresult.append(["[.] Setze ORU_Control_A_01 OnlineRemoteUpdateControlA auf 4", ""])
    hil.ORU_Control_A_01__OnlineRemoteUpdateControlA__value.set(4)

    testresult.append(["[.] setze ORU_Control_D_01 OnlineRemoteUpdateControlD auf 4", ""])
    hil.ORU_Control_D_01__OnlineRemoteUpdateControlD__value.set(4)

    testresult.append(["[.] Waehlhebelposition P aktiviert", ""])
    descr, verdict = func_gs.changeDrivePosition('P')
    testresult.append(["\xa0" + descr, verdict])

    testresult.append(["[.] VDSO_Vx3d = 32766 (0 km/h) Senden", ""])
    descr, verdict = func_gs.setVelocity_kmph(0)
    testresult.append(["\xa0" + descr, verdict])

    testresult.append(["[.] Setze PropulsionSystemActive auf 0 (NotAktiv) ", ""])
    hil.OBD_04__MM_PropulsionSystemActive__value.set(0)

    testresult.append(["[.] Setze Systeminfo_01_SI_NWDF_30 auf 1", ""])
    hil.Systeminfo_01__SI_NWDF_30__value.set(1)

    hil.cl30_on__.set(1)
    hil.cl15_on__.set(1)
    canape_diag = testenv.getCanapeDiagnostic()

    testresult.append(["[.] Tester Present deaktivieren", ""])
    canape_diag.disableTesterPresent()

    testresult.append(["[.] Lese Botschaft Waehlhebel_04::WH_Fahrstufe", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=hil.Waehlhebel_04__WH_Fahrstufe__value.get(),
            nominal_status=15,
            equal=False,
            descr="Pr�fe WH_Fahrstufe != 15 ist"))

    testresult.append(["[.] Schalte KL 15 aus and RBS aus", ""])
    hil.ClampControl_01__KST_KL_15__value.set(0)
    hil.cl15_on__.set(0)

    time.sleep(0.120)
    func_nm.hil_ecu_tx_off_state("aus")
    time.sleep(2)

    testresult.append(["[.] Fehlerspeicher l�schen", ""])
    testresult.append(canape_diag.resetEventMemory())

    testresult.append(["[.] Warte 16sec und pr�fe Busruhe", ""])
    time.sleep(16)

    testresult.append(basic_tests.checkRange(value=hil.cc_mon__A,
                                  min_value=0.0,  # 0mA
                                  max_value=0.006,  # 6mA
                                  descr="Pr�fe, dass Strom zwischen 0mA und 6mA liegt",))

    testresult.append(["[#0] Starte Testprozess: {}".format(testenv.script_name.split('.py')[0]), ""])

    # test step 1
    testresult.append(["[.] Schalte Kl.30 ein und starte RBS  warte bis erste NM Botschaft empf�ngt. ", ""])
    hil.cl15_on__.set(1)
    func_nm.hil_ecu_e2e(allstate=1, sisft=1, otamc=1, oruA=1, ourD=1)
    result = func_nm.is_bus_started()
    testresult.append(result)

    # test step 1.1
    testresult.append(["[+] Warte 2500ms. (Wechsel nach Normal State)", ""])
    time.sleep(2.500)

    # test step 1.2
    testresult.append(["[.] Programming-Precondition (0x31 0x01 0x02 0x03) pr�fen. ", ""])
    checkProgrammingPrecondition(exp_content=[])

    # test step 2
    testresult.append(["[-] Halte RU_Control_D_01_BZ.", ""])
    hil.ORU_Control_D_01__ORU_Control_D_01_BZ__switch.set(1)

    # test step 3
    testresult.append(["[.] Warte 2 Zyklen lang (2x320=640ms)", ""])
    time.sleep(0.640)

    # test step 4
    testresult.append(["[.]  Sende einmal ORU_Cotrol_D_01_CRC Fehler (Wechsel nach Safe State)", ""])
    sec = 0.315
    timeout = sec + t()
    CRC_value = hil.ORU_Control_D_01__ORU_Control_D_01_CRC__value.get()

    hil.ORU_Control_D_01__ORU_Control_D_01_CRC__value.set(0)
    while timeout > t():
        hil.ORU_Control_D_01__ORU_Control_D_01_CRC__value.set(0)

    hil.ORU_Control_D_01__ORU_Control_D_01_CRC__value.set(CRC_value)

    # test step 5
    testresult.append(["[.] Warte 220ms (FR)", ""])
    time.sleep(0.220)

    # test step 6
    testresult.append(["[.] Programming-Precondition (0x31 0x01 0x02 0x03) pr�fen. ", ""])
    checkProgrammingPrecondition(exp_content=[0xA7])

    # test step 7
    testresult.append(["[.] Warte weitere 7 Zyklen lang (insgesamt Qualifikationszeit f�r BZ Failure DTC Eintrag = n-q+ 1= 9 fehlende Botschaften im FIFO) ",""])
    time.sleep(0.320 * 7 + 0.200)

    # test step 8
    testresult.append(["[.] Programming-Precondition (0x31 0x01 0x02 0x03) pr�fen. ", ""])
    checkProgrammingPrecondition(exp_content=[0xA7])

    # test step 9
    testresult.append(["[.] Lese Fehlerspeicher aus", ""])
    testresult.append(canape_diag.checkEventMemory(aktiv_dtc_bz))

    # test step 10
    testresult.append(["[.] Setze  ORU_Control_D_01_BZ  wider fort und warte 1600ms + Toleranze (n/2 g�ltige signal im FIFO)",""])
    hil.ORU_Control_D_01__ORU_Control_D_01_BZ__switch.set(0)
    time.sleep(1.600 + 0.500)

    # test step 11
    testresult.append(["[.] Programming-Precondition (0x31 0x01 0x02 0x03) pr�fen und Lese Fehlerspeicher aus  ", ""])
    checkProgrammingPrecondition(exp_content=[])
    testresult.append(canape_diag.checkEventMemory(passiv_dtc_bz))

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[-] Test Nachbedingungen", ""])
    testresult.append(["[-] ECU ausschalten", ""])
    testenv.shutdownECU()


finally:
    # #########################################################################
    testenv.breakdown(ecu_shutdown=True)