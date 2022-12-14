# *****************************************************************************
# -*- coding: latin-1 -*-
# File    : ReadDataByIdentifierProgrammingPreconditions.py
# Title   : ReadDataByIdentifierProgrammingPreconditions
# Task    : Test for Diagnosejob 0x22 0x0448
#
# Author  : Mohammed Abdul Karim
# Date    : 22.04.2022
# Copyright 2022 Eissmann Automotive Deutschland GmbH
#
# *****************************************************************************
# ******************************** Version ************************************
# *****************************************************************************
# Rev. | Date       | Name         | Description
# -----------------------------------------------------------------------------
# 1.0  | 22.04.2022 | Mohammed   | initial
# 1.2  | 12.05.2022 | Mohammed  | Added Testschritte
# *****************************************************************************

# Imports #####################################################################
from _automation_wrapper_ import TestEnv
from ttk_checks import basic_tests
from result_list import ResultList  # @UnresolvedImport (in test_support libs)

from functions_diag import HexList, ResponseDictionaries  # @UnresolvedImport
from diag_identifier import identifier_dict  # @UnresolvedImport
import functions_common

# Instantiate test environment
testenv = TestEnv()

try:
    # #########################################################################
    # Testenv #################################################################
    testenv.setup()
    testresult = testenv.getResults()

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_358")

    # Initialize functions ####################################################
    hil = testenv.getHil()
    func_common = functions_common.FunctionsCommon(testenv)
    rd = ResponseDictionaries()

    # Initialize variables ####################################################
    test_data = identifier_dict['Programming_preconditions']
    _, all_resp = rd.Programming_preconditions()

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] ECU einschalten: KL30 an und KL15 aus", ""])
    #testenv.startupECU()
    hil.cl30_on__.set(1)
    hil.cl15_on__.set(0)

    canape_diag = testenv.getCanapeDiagnostic()
    testresult.append(["[.] Aktiviere Tester Present", ""])
    canape_diag.enableTesterPresent()

    # TEST PROCESS ############################################################
    testresult.append(["\n Starte Testprozess: {}".format(testenv.script_name.split('.py')[0]), ""])
    # silently go one chapter level up
    testresult.append(["[-0]", ""])

    # test step 1
    testresult.append(["[.] Diagnose Request schicken: 0x22 {} (Lese {})"
                      .format(HexList(test_data['identifier']), test_data['name']),
                       ""])
    request = [0x22] + test_data['identifier']
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    # test step 2
    testresult.append(["[.] ?berpr?fen, dass Request positiv beantwortet wird", ""])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    # test step 3
    testresult.append(["[.] Datenl?nge ?berpr?fen", ""])
    testresult.append(canape_diag.checkDataLength(response, test_data['exp_data_length']))

    # test step 4
    testresult.append(["[.] Inhalt der Response ?berpr?fen", ""])
    response_content = response[3:]

    preconditions_count = response_content[0]
    preconditions_list = response_content[1:]

    # test step 4.1
    testresult.append(["[+] Vergleiche erste Byte mit Responsel?nge", ""])
    testresult.append(
        basic_tests.checkStatus(
            current_status=preconditions_count,
            nominal_status=len(preconditions_list),
            descr="Pr?fe, dass erstes Byte (0x{:02X}) und Anzahl an Preconditions ?bereinstimmt"
                .format(preconditions_count)))

    # test step 4.2
    testresult.append(['[.] Pr?fe aufgelistete Preconditions', ''])
    subresult = ResultList()
    exp_list = test_data['expected_response']
    for precond in preconditions_list:
        precond_name = all_resp.get(precond, "Unbekannte Precondition")
        if precond in exp_list:
            subresult.append(["Expected precondition found in response: 0x{:02X} ({})"
                             .format(precond, precond_name, ),
                              "PASSED"])
            exp_list.remove(precond)
        else:
            subresult.append(["Precondition is not expected: 0x{:02X} ({})"
                             .format(precond, precond_name),
                              "FAILED"])

    # if exp_list:
    #     for precond in exp_list:
    #         precond_name = all_resp.get(precond, "Unbekannte Precondition")
    #         subresult.append(["Expected Precondition not found in Response: 0x{:02X} ({})"
    #                          .format(precond, precond_name),
    #                           "FAILED"])

    testresult.enableEcho(False)
    testresult.append(subresult.getCombinedResult())
    testresult.enableEcho(True)

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[-] Test Nachbedingungen", ""])
    testresult.append(["[+] ECU ausschalten", ""])
    testenv.shutdownECU()

    # cleanup #################################################################
    hil = None

finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################

print "Done."
