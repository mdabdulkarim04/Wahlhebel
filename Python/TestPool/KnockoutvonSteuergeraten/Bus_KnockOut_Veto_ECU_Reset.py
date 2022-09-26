#******************************************************************************
# -*- coding: latin-1 -*-
#
# File    : Bus_KnockOut_Veto_ECU_ResetN.py
# Title   : Bus KnockOut Veto ECU Reset
# Task    : Bus KnockOut Veto ECU Reset

# Author  : Devangbhai Patel
# Date    :  05.01.2022
# Copyright 2021 Eissmann Automotive Deutschland GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0  | 05.01.2022 | Devangbhai   | initial
# 1.1  | 10.02.2022 | Devangbhai | Rework according to new specification
# 1.2  | 04.03.2022 | Devangbhai | Added sleep time to adjust the time delay

#******************************************************************************
#
# Imports #####################################################################
from _automation_wrapper_ import TestEnv
from functions_diag import HexList
from diag_identifier import identifier_dict
import functions_common
from ttk_checks import basic_tests
import functions_gearselection
import time
from time import time as t
import functions_nm
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

    # Initialize variables ####################################################
    diag_ident_KN_CTR = identifier_dict['Knockout_counter']
    diag_ident_KN_TMR = identifier_dict['Knockout_timer']
    diag_ident_KN_TEST_MODE = identifier_dict['Knockout_test_mode']
    func_nm = functions_nm.FunctionsNM(testenv)

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_275")

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] Starte ECU (KL30 an, KL15 an)", ""])
    testenv.startupECU()
    canape_diag = testenv.getCanapeDiagnostic()

    testresult.append(["[.] Wechsle in die Extended Session", ""])
    testresult.extend(canape_diag.changeAndCheckDiagSession('extended'))

    testresult.append(["[.] BusKnockOut_Tmr und ECUKnockOut_Tmr auf 15 setzen"])
    request = [0x2E] + diag_ident_KN_TMR['identifier'] + [0x0F, 0x0F]
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    testresult.append(["�berpr�fen, dass Request positiv beantwortet wird", "INFO"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    testresult.append(["[.] BusKnockOut_Ctr und ECUKnockOut_Ctr auf 0 setzen"])
    request = [0x2E] + diag_ident_KN_CTR['identifier'] + [0x00, 0x00]
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    testresult.append(["�berpr�fen, dass Request positiv beantwortet wird", "INFO"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    testresult.append(["[.]  ECU ausschalten", ""])
    testenv.canape_Diagnostic = None
    testenv.asap3 = None
    testenv.canape_Diagnostic = None
    del (canape_diag)
    testenv.shutdownECU()

    testresult.append(["[.]  Warte 10sekund", ""])
    time.sleep(10)

    testresult.append(["[.] Starte ECU (KL30 an, KL15 an)", ""])
    testenv.startupECU()

    canape_diag = testenv.getCanapeDiagnostic()
    testresult.append(["[.] Tester Present deaktivieren", ""])
    canape_diag.disableTesterPresent()

    # TEST PROCESS ############################################################
    testresult.append(["[-] Starte Testprozess: %s" % testenv.script_name.split('.py')[0], ""])

    # test step 1
    testresult.append(["\x0a1.  In Extended Sesssion Setze BusKnockOut_Tmr auf 17, ECUKnockOut_Tmr auf 18 und NVEM coupling auf Aktive und warte 2sec"])
    testresult.append(["\xa0 Change to extended session"])
    testresult.extend(canape_diag.changeAndCheckDiagSession('extended'))

    testresult.append(["\xa0 BusKnockOut_Tmr auf 17, ECUKnockOut_Tmr auf 18 und NVEM coupling auf Aktive"])
    request = [0x2E] + diag_ident_KN_TMR['identifier'] + [0x12, 0x51]
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    testresult.append(["�berpr�fen, dass Request positiv beantwortet wird", "INFO"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))
    time.sleep(2)

    # test step 2
    testresult.append(["\x0a2.Prufe BusKnockOut_Tmr "])
    request = [0x22] + diag_ident_KN_TMR['identifier']
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    BusKnockoutTmr_start = None
    if response[0:3] == [98, 2, 203]:
        testresult.append(["Auf positive Response �berpr�fen", ""])
        testresult.append(canape_diag.checkPositiveResponse(response, request))
        BusKnockoutTmr_start = response[4]
        ECUKnockoutTmr_start = response[3]
        if BusKnockoutTmr_start and ECUKnockoutTmr_start is not None:
            if BusKnockoutTmr_start > 64:
                BusKnockoutTmr_start = BusKnockoutTmr_start - 64  # removing the active coupling value bit
                ECUKnockoutTmr_start = ECUKnockoutTmr_start
            else:
                BusKnockoutTmr_start = BusKnockoutTmr_start  # No active NVEM coupling
                ECUKnockoutTmr_start = ECUKnockoutTmr_start
        else:
            BusKnockoutTmr_start = 0
            ECUKnockoutTmr_start = 0

        testresult += [
            basic_tests.compare(left_value=BusKnockoutTmr_start, operator="<", right_value=ECUKnockoutTmr_start,
                                descr=" BusKnockOut_Tmr < ECUKnockOut_Tmr")]
    else:
        testresult.append(["Auf positive Response �berpr�fen", ""])
        testresult.append(canape_diag.checkPositiveResponse(response, request))

    # test step 3
    testresult.append(["\x0a 3.Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer "])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 17,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 17")]

    # test step 4
    testresult.append(["\x0a 4. Pr�fe BusKnockOut_Ctr"])
    request = [0x22] + diag_ident_KN_CTR['identifier']
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    BUSKnockOut_Ctr_start = None

    if response[0:3] == [98, 2, 202]:
        testresult.append(["Auf positive Response �berpr�fen", ""])
        testresult.append(canape_diag.checkPositiveResponse(response, request))
        BUSKnockOut_Ctr_start = response[4]
        if BUSKnockOut_Ctr_start is not None:
            BUSKnockOut_Ctr_start = BUSKnockOut_Ctr_start
        else:
            BUSKnockOut_Ctr_start = 0
        testresult.append(basic_tests.checkStatus(BUSKnockOut_Ctr_start, 0, descr=" BusKnockOut_Ctr = 0"))
    else:
        testresult.append(["Auf positive Response �berpr�fen", ""])
        testresult.append(canape_diag.checkPositiveResponse(response, request))

    # test step 5
    testresult.append(["\x0a 5.  Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 0,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 0x0 (Funktion nicht ausgel�st)")]

    # test step 6
    testresult.append(["\x0a 6. Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren)"
                       "Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x2 * (Veto == Active), "])

    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_1, key_1, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x02]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Pr�fe Positive Response: 0x6E 09F3 ist"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    # test step 7
    testresult.append(["\x0a7. KL15 ausschalten und 12sec warten "])
    hil.cl15_on__.set(0)
    time.sleep(12)

    # test step 8
    testresult.append( ["\x0a 8. Senden der NM Botschaft, NVEM12 und Clampcontrol von HIL--> ECU. Alle anderen Botschaften stoppen."])
    func_nm.hil_ecu_tx_signal_state_for_Knockout()
    hil.NVEM_12__period.setState("an")

    # test step 9
    testresult.append(["\x0a 9.Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer "])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 17,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 17")]

    # test step 10
    testresult.append(["\x0a 10.Pr�fe Bus State"])
    req = [0x22] + diag_ident_KN_TEST_MODE['identifier']
    [response, result] = canape_diag.sendDiagRequest(req)
    testresult.append(result)

    expected_resp = [0x62] + diag_ident_KN_TEST_MODE['identifier'] + [0x02]
    testresult.append(["Bus State != Bus Sleep (Nur Veto = Aktiv)", ""])
    testresult.append(canape_diag.checkResponse(response, expected_resp))

    # test step 11
    testresult.append(["\x0a 11.Pr�fe 70 s lang, dass KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer eingefroren ist", ""])
    timerlist = []

    KN_Waehlhebel_BusKnockOutTimer = 17
    sec = 70
    timeout = sec + t()
    value_boolean = True

    while timeout > t():
        timerlist.append(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get())

    for timer_values in timerlist:
        if KN_Waehlhebel_BusKnockOutTimer != timer_values:
            value_boolean = False
            break
    testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang konstant bei %s"
                       % (sec, KN_Waehlhebel_BusKnockOutTimer), "PASSED"]) if value_boolean \
        else testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang nicht konstant bei %s"
                                % (sec, KN_Waehlhebel_BusKnockOutTimer), "FAILED"])

    # test step 12
    testresult.append(["\x0a 12.  Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 1,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 0x1 (Veto aktiv)")]

    # test step 13
    testresult.append(["\x0a 13. Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren) "
                       "Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x4 * (Supress Veto == Active) und warte 2sec"])

    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_2, key_2, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x04]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Pr�fe Positive Response: 0x6E 09F3 ist"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))
    time.sleep(2)

    # test step 14
    testresult.append(["\x0a 14. Pr�fe, dass KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer nach 1 Minute um 1 dekrementiert wird "])
    time.sleep(60)
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 16,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 16  (wird dekrementiert)")]

    # test step 15
    testresult.append(["\x0a 15.  Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 0,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 0x0 (Funktion nicht ausgel�st)")]

    # test step 16
    testresult.append(["\x0a 16. Warte bis KN_Waehlhebel:KN_Waehlhebel_BUSKnockOutTimer == 15 (Timeout: 1min)"])
    timeout = 60
    t_out = timeout + t()
    while t_out > t():
        if hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get() == 15:
            break
        elif t_out > t() == False:
            testresult.append(
                ["\xa0 KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer  hat kein auf 15 gesetz in 1min", "FAILED"])
            break

    # test step 17
    testresult.append(["\x0a 17. Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren)"
                       "Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x2 * (Veto == Active), und warte 2sec"])

    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_1, key_1, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x02]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Pr�fe Positive Response: 0x6E 09F3 ist"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))
    time.sleep(2)

    # test step 18
    testresult.append(["\x0a 18.Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer "])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 15,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 15")]

    # test step 19
    testresult.append(["\x0a 19.Pr�fe 70 s lang, dass KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer eingefroren ist", ""])
    timerlist = []

    KN_Waehlhebel_BusKnockOutTimer = 15
    sec = 70
    timeout = sec + t()
    value_boolean = True

    while timeout > t():
        timerlist.append(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get())

    for timer_values in timerlist:
        if KN_Waehlhebel_BusKnockOutTimer != timer_values:
            value_boolean = False
            break
    testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang konstant bei %s"
                       % (sec, KN_Waehlhebel_BusKnockOutTimer), "PASSED"]) if value_boolean \
        else testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang nicht konstant bei %s"
                                % (sec, KN_Waehlhebel_BusKnockOutTimer), "FAILED"])

    # test step 20
    testresult.append(["\x0a 20.  Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 1,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 0x1 (Veto aktiv)")]

    # test step 21
    testresult.append(["\x0a 21. Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren) "
                       "Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x4 * (Supress Veto == Active) und warte 2sec"])

    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_2, key_2, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x04]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Pr�fe Positive Response: 0x6E 09F3 ist"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))
    time.sleep(2)

    # test step 22
    testresult.append(["\x0a 22. Pr�fe, dass KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer nach 1 Minute um 1 dekrementiert wird "])
    time.sleep(60)
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 14,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 14  (wird dekrementiert)")]

    # tests step 23
    testresult.append(["\x0a 23.  Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 0,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 0x0 (Funktion nicht ausgel�st)")]

    # test step 24
    testresult.append(["\x0a 24. Warte bis KN_Waehlhebel:KN_Waehlhebel_BUSKnockOutTimer == 0 (Timeout: 14min)"])
    timeout = 14 * 60
    t_out = timeout + t()
    while t_out > t():
        if hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get() == 0:
            break
        elif t_out > t() == False:
            testresult.append(
                ["\xa0 KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer  hat kein auf 0 gesetz in 14min", "FAILED"])
            break
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 0,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 0 (Timer Abgelaufen)")]

    # tests step 25
    testresult.append(["\x0a 25. Pr�fe, dass nach 60 sekund Kein Reset des SG stattfindet "])
    time.sleep(60)
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 0,
                                           descr="KN_Waehlhebel_BUSKnockOut = 0")]

    # test step 26
    testresult.append(["\x0a 26. Pr�fe KN_Waehlhebel:Waehlhebel_Abschaltstufe", ""])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__Waehlhebel_Abschaltstufe__value, 0,
                                           descr="KN_Waehlhebel:Waehlhebel_Abschaltstufe  == 0 (keine_Einschraenkung)")]

    # test step 27
    testresult.append(["\x0a 27. Pr�fe NVEM_12:NVEM_Abschaltstufe", ""])
    testresult += [basic_tests.checkStatus(hil.NVEM_12__NVEM_Abschaltstufe__value, 3, equal=False,
                                           descr="NVEM_12:NVEM_Abschaltstufe__value != 3")]

    # test step 28
    testresult.append(["\x0a 28. Sende NVEM_12:NVEM_Abschaltstufe = 3 (Stufe_3) und 500ms warten", ""])
    hil.NVEM_12__NVEM_Abschaltstufe__value.set(3)
    time.sleep(0.5)

    # test step 29
    testresult.append(["\x0a 29. Pr�fe KN_Waehlhebel:Waehlhebel_Abschaltstufe", ""])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__Waehlhebel_Abschaltstufe__value, 1,
                                           descr="KN_Waehlhebel:Waehlhebel_Abschaltstufe  == 1  (Funktionseinschraenkung)")]

    # test step 30
    testresult.append(["\x0a 30.  Pr�fe, dass Reset des SG stattfindet"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 2,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 2 (0x2= Funktion_ausgeloest)")]

    # test step 31
    testresult.append(["\x0a 31. Schalte alle signal (HIL--> ECU) aus und Warte 1 min", ""])
    time.sleep(0.250)
    func_nm.hil_ecu_tx_signal_state_for_Knockout(NM_Clampcontrol_send=False, all_other_send=False)
    time.sleep(60)

    # tests tep 32
    testresult.append(["\x0a 32. Schalte alle signal (HIL--> ECU) ein. Schalte KL15 ein und warte 5sec", ""])
    hil.cl15_on__.set(1)
    func_nm.hil_ecu_tx_signal_state_for_Knockout(NM_Clampcontrol_send=True, all_other_send=True)
    time.sleep(5)

    # test step 33
    testresult.append(["\x0a 33 Pr�fe BusKnockOut_Tmr"])
    request = [0x22] + diag_ident_KN_TMR['identifier']
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    testresult.append(["Auf positive Response �berpr�fen", ""])
    testresult.append(canape_diag.checkPositiveResponse(response, request))
    BusKnockoutTmr = None
    if response[0:3] == [98, 2, 203]:
        testresult.append(["Auf positive Response �berpr�fen", ""])
        testresult.append(canape_diag.checkPositiveResponse(response, request))
        BusKnockoutTmr = response[4]
        if BusKnockoutTmr is not None:
            if BusKnockoutTmr > 64:
                BusKnockoutTmr = BusKnockoutTmr - 64  # removing the active coupling value bit
                testresult.append(["\xa0 NVEM couplling ist Aktive", "PASSED"])
            else:
                BusKnockoutTmr = BusKnockoutTmr  # No active NVEM coupling
                testresult.append(["\xa0 NVEM couplling ist inaktive", "FAILED"])
        else:
            BusKnockoutTmr = 0

        testresult += [basic_tests.checkStatus(BusKnockoutTmr, 17, descr="KN_Waehlhebel_BUSKnockOutTimer = 17")]

    # test step 34
    testresult.append(["\x0a 34 Pr�fe BusKnockOut_ctr"])
    request = [0x22] + diag_ident_KN_CTR['identifier']
    response_diag, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)
    testresult.append(["Auf positive Response �berpr�fen", ""])
    testresult.append(canape_diag.checkPositiveResponse(response_diag, request))
    ECUKnockOut_Ctr_end = None

    if response_diag[0:3] == [98, 2, 202]:
        ECUKnockOut_Ctr_end = response_diag[4]
        if ECUKnockOut_Ctr_end is not None:
            ECUKnockOut_Ctr_end = ECUKnockOut_Ctr_end
        else:
            ECUKnockOut_Ctr_end = 0

        if BUSKnockOut_Ctr_start is not None:
            testresult.append(basic_tests.checkStatus(
                current_status=ECUKnockOut_Ctr_end,
                nominal_status=1,
                descr=" BusKnockOut_ctr == 0x1 (wird inkrementiert)", ))
    else:
        testresult.append(
            ["\xa0 Kein Positive response erhalten.  BusKnockOut_Ctr kann nicht auslasen", "FAILED"])

    # test step 35
    testresult.append(["\x0a 35.Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer "])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 17,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer =  BusKnockOut_Tmr (Reset durch SG-Reset / KL15 ein) = 17")]

    # test step 36
    testresult.append(["\x0a 36. Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 2,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 2 (0x2= Funktion_ausgeloest)")]

    # test step 37
    testresult.append(["\x0a 37. Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren)"
                       "Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x2 * (Veto == Active), "])

    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_1, key_1, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x02]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Pr�fe Positive Response: 0x6E 09F3 ist"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    # tests tep 38
    testresult.append(["\x0a 38.Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer "])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 17,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 17")]
    # test step 39
    testresult.append(["\x0a 39 Pr�fe 70 s lang, dass KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer nicht l�uft", ""])
    timerlist = []
    KN_Waehlhebel_BusKnockOutTimer = 17
    sec = 70
    timeout = sec + t()
    value_boolean = True

    while timeout > t():
        timerlist.append(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get())

    for timer_values in timerlist:
        if KN_Waehlhebel_BusKnockOutTimer != timer_values:
            value_boolean = False
            break
    testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang konstant bei %s"
                       % (sec, KN_Waehlhebel_BusKnockOutTimer), "PASSED"]) if value_boolean \
        else testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang nicht konstant bei %s"
                                % (sec, KN_Waehlhebel_BusKnockOutTimer), "FAILED"])

    # test step 40
    testresult.append(["\x0a 40. Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 2,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 2 (0x2= Funktion_ausgel�st)")]

    # test step 41
    testresult.append(["\x0a 41. Wechsel in die Entwicklersession, (in Factory mode security access d�rchf�hren) "
                       "Setze mittels 2E 09 F3: KnockOut_Test_mode  auf 0x00"])

    testresult.extend(canape_diag.changeAndCheckDiagSession('factory_mode'))
    testresult.append(["\xa0 Erfolgreichen Security Access durchf�hren", "INFO"])
    seed_3, key_3, result = canape_diag.performSecurityAccess()
    testresult.extend(result)

    request = [0x2E] + diag_ident_KN_TEST_MODE['identifier'] + [0x00]
    [response, result] = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0Pr�fe Positive Response: 0x6E 09F3 ist"])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    # test step 42
    testresult.append(["\x0a 42.Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer "])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value, 17,
                                           descr="KN_Waehlhebel_BUSKnockOutTimer = 17")]

    # test step 43
    testresult.append(["\x0a 43. Pr�fe 70 s lang, dass KN_Waehlhebel:KN_Waehlhebel_BusKnockOutTimer  nicht l�uft", ""])
    timerlist = []

    KN_Waehlhebel_BusKnockOutTimer = 17
    sec = 70
    timeout = sec + t()
    value_boolean = True

    while timeout > t():
        timerlist.append(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOutTimer__value.get())

    for timer_values in timerlist:
        if KN_Waehlhebel_BusKnockOutTimer != timer_values:
            value_boolean = False
            break
    testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang konstant bei %s"
                       % (sec, KN_Waehlhebel_BusKnockOutTimer), "PASSED"]) if value_boolean \
        else testresult.append(["\xa0 KN_Waehlhebel_BusKnockOutTimer blieb %s Sekunden lang nicht konstant bei %s"
                                % (sec, KN_Waehlhebel_BusKnockOutTimer), "FAILED"])

    # test step 44
    testresult.append(["\x0a 44. Pr�fe KN_Waehlhebel:KN_Waehlhebel_BusKnockOut"])
    testresult += [basic_tests.checkStatus(hil.KN_Waehlhebel__KN_Waehlhebel_BusKnockOut__value, 2,
                                           descr=" KN_Waehlhebel:KN_Waehlhebel_BusKnockOut = 2 (0x2= Funktion_ausgel�st)")]

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[-] Test Nachbedingungen", ""])
    testresult.append(["[+] ECU ausschalten", ""])
    testenv.shutdownECU()

    # cleanup
    hil = None

finally:
    # #########################################################################
    testenv.breakdown(ecu_shutdown=False)
