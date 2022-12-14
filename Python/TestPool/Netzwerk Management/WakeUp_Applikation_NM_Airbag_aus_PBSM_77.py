#******************************************************************************
# -*- coding: latin1 -*-
# File    : WakeUp_Applikation_NM_Airbag_aus_PBSM_77.py
# Title   : WakeUp Applikation NM_Airbag aus PBSM
# Task    : A minimal "WakeUp_Applikation_NM_Airbag_aus_PBSM!" test script
#
# Copyright 2020 Eissmann Automotive Deutschland GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0  | 21.01.2021 | Mohammed     | initial
# 1.1  | 02.06.2021 | StengerS     | reworked
# 1.2  | 30.06.2021 | NeumannA     | evaluation of FCAB Value updated
# 1.3  | 30.07.2021 | Mohammed     | Added 2.1 and 2.2 TestSteps
# 1.4  | 09.09.2021 | Mohammed     | Added Fehler Id
# 1.5  | 09.11.2021 | Devangbhai   | Reworked
# 1.6  | 10.11.2021 | Devangbhai   | Reworked
# 1.7  | 10.11.2021 | Mohammed     | Added NM_Waehlhebel_CBV_AWB Right Value
# 1.8  | 24.11.2021 | Devangbhai   | changed waiting time from 500ms to 300ms
# 1.9  | 21.12.2021 | Mohammed     | Added Fehler Id
# 1.10 | 17.02.2022 | Devangbhai   | Corrected the evaluation value of NM_Waehlhebel_NM_aktiv_KL15 and NM_Waehlhebel_NM_aktiv_Tmin
# 1.11 | 07.03.2022 | Mohammed     | Step 8. Adedde Sleep time 200ms before NM_Waehlhebel_NM_aktiv_Tmin Signal
# 1.12 | 08.03.2022 | Devangbhai   | Removed 20ms cycle time

#******************************************************************************

import time
from _automation_wrapper_ import TestEnv
from ttk_daq import eval_signal
from ttk_checks import basic_tests
import functions_nm
import functions_gearselection
import copy
from functions_nm import _checkStatus

# Instantiate test environment
testenv = TestEnv()

try:
    # #########################################################################
    # Testenv #################################################################
    testenv.setup()
    testresult = testenv.getResults()

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_77")

    # Initialize functions ####################################################
    hil = testenv.getHil()
    daq = testenv.getGammaDAQ()
    func_gs = functions_gearselection.FunctionsGearSelection(testenv, hil)
    func_nm = functions_nm.FunctionsNM(testenv)

    # Initialize variables ####################################################
    applikationsbotschaften = [hil.Waehlhebel_04__timestamp,
                               hil.DS_Waehlhebel__timestamp,
                               hil.KN_Waehlhebel__timestamp, ]

    nm_botschaften = [hil.NM_Waehlhebel__timestamp]
    messages_cycle_times = {str(hil.Waehlhebel_04__timestamp): 10,
                            str(hil.DS_Waehlhebel__timestamp): 1000,
                            str(hil.KN_Waehlhebel__timestamp): 500,
                            str(hil.NM_Waehlhebel__timestamp): 200,
                            }
    tolerance_percent = 0.10
    cycletime_tol_perc = 0.10
    ttimeout = 1.0
    ttimeout_tol_perc = 0.05
    nm_stop_s = 0.4
    t_send_after_wakeup = 0.15  # to be clarified


    meas_vars = [hil.cl15_on__, hil.Waehlhebel_04__timestamp,
                 hil.DS_Waehlhebel__timestamp, hil.KN_Waehlhebel__timestamp,
                 hil.NM_Waehlhebel__timestamp, hil.NM_Airbag__NM_Airbag_01_FCAB__value]

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] ECU einschalten und 4 Sekunden warten (T_aktiv_min)", ""])
    testenv.startupECU()
    time.sleep(4)

    # TEST PROCESS ############################################################
    testresult.append(["[-] Starte Testprozess: %s" % testenv.script_name.split('.py')[0], ""])
    testresult.append(["[+0]", ""])

    testresult.append(["Starte DAQ Messung f?r Applikations- und NM-Botschaften", "INFO"])
    testresult.append(["Folgende Signale werden mitgemessen:\n%s" % meas_vars, "INFO"])
    daq.startMeasurement(meas_vars)

    testresult.append(["\x0a1. Pr?fe Werte der Botschaft NM_Waehlhebel", ""])

    testresult += [
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_CBV_AWB__value, 0,
                                descr="NM_Waehlhebel_CBV_AWB:Passiver_WakeUp"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_CBV_CRI__value, 1,
                                descr="NM_Waehlhebel_CBV_CRI:NM_mit_Clusteranforderungen"),
        func_nm.checkFcabBitwise(hil.NM_Waehlhebel__NM_Waehlhebel_FCAB__value.get(), [12], [],
                                 descr="NM_Waehlhebel_FCAB:12_GearSelector"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_SNI_10__value, 83,
                                descr="NM_Waehlhebel_SNI_10:Waehlhebel_SNI"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_NM_State__value, 4 or 8 ,
                                descr="NM_Waehlhebel_NM_State:NM_NO_aus_RM oder NM_NO_aus_RS"), # added right value
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_Wakeup_V12__value, 1,
                                descr="NM_Waehlhebel_Wakeup_V12:Bus_Wakeup"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_NM_aktiv_KL15__value, 1,
                                descr="NM_Waehlhebel_NM_aktiv_KL15:KL15_EIN"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_NM_aktiv_Diag__value, 0,
                                descr="NM_Waehlhebel_NM_aktiv_Diag:Inaktiv"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_NM_aktiv_Tmin__value, 0,
                                descr="NM_Waehlhebel_NM_aktiv_Tmin:Inaktiv"),
        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Aktiv_N_Haltephase_abgelaufen__value, 0,
                                descr="NM_Aktiv_N_Haltephase_abgelaufen= 0 (Inaktiv)", )
    ]
    testresult.append(
        _checkStatus(current_status=hil.NM_Waehlhebel__NM_Waehlhebel_UDS_CC__value,
                     nominal_status=0,
                     descr="NM_Waehlhebel_UDS_CC:Inaktiv is",
                     ticket_id='FehlerId:EGA-PRM-13')
    )

    time.sleep(2)

    testresult.append(["Stoppe DAQ Messung", "INFO"])
    daq_data = daq.stopMeasurement()
    time.sleep(0.1)
    hcp1_mess = eval_signal.EvalSignal(daq_data[str(meas_vars[5])])
    hcp1_mess.clearAll()
    t_hcp1_sent = hcp1_mess.getTime()

    idx_hcp1_sent = hcp1_mess.cur_index

    daq_data_part1 = copy.deepcopy(daq_data)
    daq_data_part2 = copy.deepcopy(daq_data)
    for data1, data2 in zip(daq_data_part1, daq_data_part2):
        daq_data_part1[data1]['data'] = daq_data_part1[data1]['d' \
                                                              'ata'][:idx_hcp1_sent]
        daq_data_part1[data1]['time'] = daq_data_part1[data1]['time'][:idx_hcp1_sent]
        daq_data_part2[data2]['data'] = daq_data_part2[data2]['data'][idx_hcp1_sent:]
        daq_data_part2[data2]['time'] = daq_data_part2[data2]['time'][idx_hcp1_sent:]

    testresult.append(["\x0a2. Pr?fe Versenden (Timestamps/Zykluszeit) der gesendeten Applikations- und NM Botschaften:", ""])
    for var in meas_vars:
        if (var != hil.cl15_on__) and (var != hil.NM_Airbag__NM_Airbag_01_FCAB__value):
            cycle_times, wakeup_time = func_nm.analyseCycleSleepTimes(start_time=t_hcp1_sent, daq_data=daq_data_part2[str(var)])

            if len(cycle_times) > 0:
                if var == hil.NM_Waehlhebel__timestamp:
                    testresult.append(["\xa0Pr?fe, dass Zykluszeit von NM-Botschaft: NM_Waehlhebel korrekt ist", ""])
                    cycle_time = sum(cycle_times) / len(cycle_times)
                    testresult.append(basic_tests.checkTolerance(current_value=cycle_time, rated_value=messages_cycle_times[str(var)], rel_pos=cycletime_tol_perc, descr="Zykluszeit von %s" % str(var)))
                else:
                    testresult.append(["\xa0Pr?fe, dass Zykluszeit von Applikationsbotschaften korrekt ist", ""])
                    cycle_time = sum(cycle_times) / len(cycle_times)
                    testresult.append( basic_tests.checkTolerance( current_value=cycle_time, rated_value=messages_cycle_times[str(var)], rel_pos=cycletime_tol_perc, descr="Zykluszeit von %s" % str(var)))
            else:
                testresult.append( ["%s Botschaft beginnt sendet nicht" % str(var), "FAILED"])


    testresult.append(["Starte DAQ Messung f?r Applikations- und NM-Botschaften", "INFO"])
    testresult.append(["Folgende Signale werden mitgemessen:\n%s" % meas_vars, ""])
    daq.startMeasurement(meas_vars)
    time.sleep(2)

    testresult.append(["\x0a3. Schalte KL15 aus (=0), Schalte Restbussimulation aus, 150ms warten", ""])
    hil.cl15_on__.set(0)
    sleeping_t = 0.030
    time.sleep(sleeping_t)
    func_nm.hil_ecu_tx_off_state("aus")
    # descr, verdict = func_gs.switchAllRXMessagesOff()
    # testresult.append([descr, verdict])
    time.sleep(0.15 - sleeping_t)

    testresult.append(["Warte 1000ms (T Timeout)", "INFO"])
    time.sleep(1)

    testresult.append(["Warte 300ms (< T WaitBusSleep)", "INFO"])
    time.sleep(0.3)

    testresult.append(["HCP1 NM-Botschaft mit NM_Airbag_01_FCAB = 12_GearSelector senden", "INFO"])
    hil.NM_Airbag__NM_Airbag_01_FCAB__value.set(2048)  # 12
    hil.NM_Airbag__period.setState('an')

    testresult.append(["Pr?fe erneut Werte der Botschaft NM_Waehlhebel", "INFO"])
    NM_Waehlhebel_FCAB =             func_nm.checkFcabBitwise(hil.NM_Waehlhebel__NM_Waehlhebel_FCAB__value.get(), [12], [], descr="NM_Waehlhebel_FCAB:12_GearSelector")   # TODO check 1st message
    time.sleep(.200)
    NM_Waehlhebel_CBV_CRI  =         basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_CBV_CRI__value, 1, descr="NM_Waehlhebel_CBV_CRI:NM_mit_Clusteranforderungen")
    NM_Waehlhebel_SNI_10 =           basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_SNI_10__value, 83, descr="NM_Waehlhebel_SNI_10:Waehlhebel_SNI")
    NM_Waehlhebel_UDS_CC =           _checkStatus(current_status=hil.NM_Waehlhebel__NM_Waehlhebel_UDS_CC__value, nominal_status=0,descr="NM_Waehlhebel_UDS_CC:Inaktiv ist", ticket_id='Fehler Id:EGA-PRM-13')
    NM_Waehlhebel_Wakeup_V12 =       basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_Wakeup_V12__value, 1, descr="NM_Waehlhebel_Wakeup_V12:Bus_Wakeup")
    NM_Waehlhebel_NM_aktiv_Diag =    basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Waehlhebel_NM_aktiv_Diag__value, 0, descr="NM_Waehlhebel_NM_aktiv_Diag:Inaktiv")
    N_Haltephase_abgelaufen =        basic_tests.checkStatus(hil.NM_Waehlhebel__NM_Aktiv_N_Haltephase_abgelaufen__value, 0, descr="NM_Aktiv_N_Haltephase_abgelaufen= 0 (Inaktiv)", )
    NM_Waehlhebel_CBV_AWB =          _checkStatus( current_status=hil.NM_Waehlhebel__NM_Waehlhebel_CBV_AWB__value, nominal_status=0, descr="NM_Waehlhebel_CBV_AWB:Passiver_WakeUp ist", ticket_id='Fehler Id:EGA-PRM-13')
    NM_RM_aus_PBSM =                 _checkStatus( current_status=hil.NM_Waehlhebel__NM_Waehlhebel_NM_State__value, nominal_status=2, descr="NM_RM_aus_PBSM:NM_RM_aus_PBSM ist", ticket_id='Fehler Id:EGA-PRM-13' )
    NM_aktiv_Tmin =                  _checkStatus( current_status=hil.NM_Waehlhebel__NM_Waehlhebel_NM_aktiv_Tmin__value, nominal_status=1, descr="NM_aktiv_Tmin:Mindestaktivzeit ist ", ticket_id='Fehler Id:EGA-PRM-13')
    NM_Waehlhebel_NM_aktiv_KL15 =    _checkStatus( current_status=hil.NM_Waehlhebel__NM_Waehlhebel_NM_aktiv_KL15__value,nominal_status=0, descr="NM_Waehlhebel_NM_aktiv_KL15:Inaktiv ist", ticket_id='Fehler Id:EGA-PRM-13')
    time.sleep(3)

    testresult.append(["Stoppe DAQ Messung", "INFO"])
    daq_data1 = daq.stopMeasurement()

    plot_data = {}
    for mes in applikationsbotschaften + nm_botschaften:
        plot_data[str(mes)] = daq_data1[str(mes)]
    testresult.append(daq.plotMultiShot(plot_data, "WakeUp_Applikation_NM_Airbag_aus_PBSM_77") )

    testresult.append(["\xa0Werte KL15 Signal aus", "INFO"])
    descr, plot, verdict = daq.plotSingleShot( daq_data=daq_data1[str(meas_vars[0])], filename="WakeUp_Applikation_NM_Airbag_aus_PBSM_77_KL_15", label_signal="KL15" )
    testresult.append([descr, plot, verdict])

    testresult.append(["\xa0Werte NM_Airbag Signal aus", "INFO"])
    descr, plot, verdict = daq.plotSingleShot(
        daq_data=daq_data1[str(meas_vars[5])],
        filename="WakeUp_Applikation_NM_Airbag_aus_PBSM_77_Airbag",
        label_signal="NM_Airbag_FCAB")
    testresult.append([descr, plot, verdict])

    # DAQ Analysis ################################################################
    testresult.append(["\x0aAnalysiere DAQ Messung", "INFO"])

    cl15_data = daq_data1[str(hil.cl15_on__)]
    cl_15 = eval_signal.EvalSignal(cl15_data)
    cl_15.clearAll()
    time_zero = cl_15.getTime()
    # find timestamp when clamp 15 is switched off:
    t_cl_15_off = cl_15.findNext("==", 0)
    cl15_idx = cl_15.cur_index  # read index
    testresult.append(["Ermittelter Zeitpunkt 'KL15 aus': %s" % (t_cl_15_off - time_zero), "INFO"])
    test_start_time = cl15_data['time'][cl15_idx-200]  # go 200ms back (Zykluszeit NM)
    testresult.append(["Start-Zeitpunkt Analyse (200ms vorher): %ss" % (test_start_time - time_zero), "INFO"])

    airbag_mess = eval_signal.EvalSignal(daq_data1[str(meas_vars[5])])
    airbag_mess.clearAll()
    time_zero = airbag_mess.getTime()
    # find timestamp when Airbag message is sent:
    t_airbag_sent = airbag_mess.findNext("==", 2048)
    testresult.append(["Ermittelter Zeitpunkt 'Senden der NM_Airbag Botschaft': %s" % (t_airbag_sent - time_zero), "INFO"])

    idx_airbag_sent = airbag_mess.cur_index  # index, when KL15 is switched on
    # prepare daq data for first analyse (behaviour till nm airbag will send)
    daq_data_part1 = copy.deepcopy(daq_data1)
    daq_data_part2 = copy.deepcopy(daq_data1)
    for data1, data2 in zip(daq_data_part1, daq_data_part2):
        daq_data_part1[data1]['data'] = daq_data_part1[data1]['data'][:idx_airbag_sent]
        daq_data_part1[data1]['time'] = daq_data_part1[data1]['time'][:idx_airbag_sent]
        daq_data_part2[data2]['data'] = daq_data_part2[data2]['data'][idx_airbag_sent:]
        daq_data_part2[data2]['time'] = daq_data_part2[data2]['time'][idx_airbag_sent:]


    # Check that messages stop sending correctly #####################################
    cycle_times = {}
    sleep_times = {}
    for var in meas_vars:
        if (var != hil.cl15_on__) and (var != hil.NM_Airbag__NM_Airbag_01_FCAB__value):
            cycle_time, sleep_time = func_nm.analyseCycleSleepTimes(
                start_time=test_start_time,
                daq_data=daq_data_part1[str(var)])
            cycle_times[str(var)] = cycle_time
            sleep_times[str(var)] = sleep_time

    testresult.append(["\x0a4 Pr?fe Versenden (Timestamps/Zykluszeit) der gesendeten Applikations- und NM Botschaften", ""])
    testresult.append(["\x0a4.1 Pr?fe NM-Botschaften werden nicht gesendet: NM_Waehlhebel keine timestamps", ""])
    for var in nm_botschaften:
        st_nm = sleep_times[str(var)]
        if st_nm:
            testresult.append(
                basic_tests.compare(
                    left_value=st_nm,
                    operator="<=",
                    right_value=nm_stop_s,
                    descr = "Vergleiche Stop NM Botschaft <= %ss"%nm_stop_s
                )
            )
        else:
            testresult.append(["Keine Einschlafzeit f?r NM-Botschaften gefunden", "FAILED"])

        testresult.append(["\x0a4.2 Applikationsbotschaften: Waehlhebel_04, KN_Waehlhebel, DS_Waehlhebel  werden gesendet", ""])
        for var in applikationsbotschaften:
            ct = cycle_times[str(var)]
            if len(ct) > 0:
                testresult.append(["\xa0Pr?fe, dass Zykluszeit korrekt ist", ""])
                cycle_time = sum(ct) / len(ct)
                testresult.append(
                    basic_tests.checkTolerance(
                        current_value=cycle_time,
                        rated_value=messages_cycle_times[str(var)],
                        rel_pos=cycletime_tol_perc,
                        descr="Zykluszeit von %s"%str(var)
                    )
                )
            else:
                testresult.append(["Nicht genug Zykluszeiten (%s) gemessen um Zeitpunkt zu analysieren"%str(var), "FAILED"])

    testresult.append(["\x0a5. Warte 1000ms (T Timeout)", ""])
    testresult.append(["\x0a 6. Warte 500ms (< T WaitBusSleep)", ""])
    testresult.append(["\x0a 7.HCP1 NM-Botschaft mit NM_Airbag_01_FCAB = 12_GearSelector senden und 200ms warten", ""])
    testresult.append(["\x0a 8.NM_Waehlhebel Botschaft auslesen", ""])
    testresult.append(NM_Waehlhebel_CBV_CRI)
    testresult.append(NM_Waehlhebel_FCAB)
    testresult.append(NM_Waehlhebel_SNI_10)
    testresult.append(NM_Waehlhebel_UDS_CC)
    testresult.append(NM_Waehlhebel_Wakeup_V12)
    testresult.append(NM_Waehlhebel_NM_aktiv_Diag)
    testresult.append(NM_Waehlhebel_CBV_AWB)
    testresult.append(NM_RM_aus_PBSM)
    testresult.append(NM_Waehlhebel_NM_aktiv_KL15)
    testresult.append(NM_aktiv_Tmin)
    testresult.append(N_Haltephase_abgelaufen)

    # Check when messages start sending again #####################################
    testresult.append(["\x0a9. Pr?fe Versenden (Timestamps/Zykluszeit) der gesendeten Applikations- und NM Botschaften", ""])
    wakeup_times = {}
    for var in meas_vars:
        if (var != hil.cl15_on__) and (var != hil.NM_Airbag__NM_Airbag_01_FCAB__value):
            cycle_times, wakeup_time = func_nm.analyseCycleWakeupTimes(
                start_time=t_airbag_sent - 0.001,
                daq_data=daq_data_part2[str(var)])
            wakeup_times[str(var)] = wakeup_time

            # if wakeup_time:
            #     testresult.append(["\xa0Pr?fe, dass Botschaft %s nach 'Senden der NM_Airbag Botschaft' werden gesendet " % str(var), ""])
            #     testresult.append(
            #         basic_tests.checkRange(
            #             value=wakeup_time,
            #             min_value=0,  # 0 means 'immediately'
            #             max_value=0 + t_send_after_wakeup,
            #             descr="Zeit von %s nach KL15 an" % str(var),
            #         )
            #     )
            # else:
            #     testresult.append(["%s beginnt nach 'Senden der NM_Airbag Botschaft' nicht an zu senden" % str(var), "FAILED"])

            if len(cycle_times) > 0:
                if var == hil.NM_Waehlhebel__timestamp:
                    if len(cycle_times) > 11:
                        # testresult.append(["\xa0Pr?fe, dass erste 10 Zykluszeiten nach erneutem Senden korrekt sind", ""])
                        # cycle_times_first_10 = cycle_times[:10]
                        # cycle_time = sum(cycle_times_first_10) / len(cycle_times_first_10)
                        # testresult.append(
                        #     basic_tests.checkTolerance(
                        #         current_value=cycle_time,
                        #         rated_value=messages_cycle_times[str(var)]/10,
                        #         rel_pos=cycletime_tol_perc,
                        #         descr="Zykluszeit von %s" % str(var)
                        #         )
                        #     )
                        testresult.append(["\xa0Pr?fe, dass  Zykluszeiten korrekt sind", ""])
                        # cycle_times_next = cycle_times[10:]
                        cycle_time = sum(cycle_times) / len(cycle_times)
                        testresult.append(
                            basic_tests.checkTolerance(
                                current_value=cycle_time,
                                rated_value=messages_cycle_times[str(var)],
                                rel_pos=cycletime_tol_perc,
                                descr="Zykluszeit von %s" % str(var)
                                )
                            )
                    else:
                        testresult.append(
                            ["Nicht genug Zykluszeiten aufgezeichnet zum Auswerten (min. 11: 10 fast, 1 normal)",
                             "FAILED"])
                else:
                    testresult.append(["\xa0Pr?fe, dass Zykluszeit nach erneutem Senden korrekt ist", ""])
                    cycle_time = sum(cycle_times) / len(cycle_times)
                    testresult.append(
                        basic_tests.checkTolerance(
                            current_value=cycle_time,
                            rated_value=messages_cycle_times[str(var)],
                            rel_pos=cycletime_tol_perc,
                            descr="Zykluszeit von %s" % str(var)
                            )
                        )
            else:
                testresult.append(["%s Botschaft beginnt nicht wieder zu senden, nachdem NM_Airbag wieder sendet"%str(var), "FAILED"])


    # Check that NM messages is sent first #####################################
    testresult.append(["\x0aPr?fe, dass NM-Botschaften vor der Applikationsbotschaft gesendet wird", ""])

    # Check that NM message is sent as first ##################################
    if ((wakeup_times[str(hil.NM_Waehlhebel__timestamp)] < wakeup_times[str(hil.Waehlhebel_04__timestamp)]) and
        (wakeup_times[str(hil.NM_Waehlhebel__timestamp)] <= wakeup_times[str(hil.DS_Waehlhebel__timestamp)]) and
        (wakeup_times[str(hil.NM_Waehlhebel__timestamp)] <= wakeup_times[str(hil.KN_Waehlhebel__timestamp)])):
        descr = "NM-Botschaft wird zuerst gesendet. \nNM NM_Waehlhebel__timestamp = %s, Waehlhebel_04__timestamp= %s, DS_Waehlhebel__timestamp= %s, KN_Waehlhebel__timestamp = %s" % (wakeup_times[str(hil.NM_Waehlhebel__timestamp)], wakeup_times[str(hil.Waehlhebel_04__timestamp)],wakeup_times[str(hil.DS_Waehlhebel__timestamp)], wakeup_times[str(hil.KN_Waehlhebel__timestamp)])
        verdict = "PASSED"
    else:
        descr = "NM-Botschaft wird NICHT zuerst gesendet. \nNM NM_Waehlhebel__timestamp = %s, Waehlhebel_04__timestamp= %s, DS_Waehlhebel__timestamp= %s, KN_Waehlhebel__timestamp = %s" %(wakeup_times[str(hil.NM_Waehlhebel__timestamp)], wakeup_times[str(hil.Waehlhebel_04__timestamp)], wakeup_times[str(hil.DS_Waehlhebel__timestamp)], wakeup_times[str(hil.KN_Waehlhebel__timestamp)])
        verdict = "FAILED"

    testresult.append([descr, verdict])
    # testresult.append(["[-0]", ""])

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[-] Test Nachbedingungen", ""])
    testresult.append(["Shutdown ECU", ""])
    testenv.shutdownECU()

    # cleanup
    hil = None

finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################
