# ******************************************************************************
# -*- coding: latin1 -*-
# File    : Diagnose_VW_logical_software_block_lock_value.py
# Title   : Diagnose VW logical software block lock value
# Task    : Test for diag identifier 040F
#
# Author  : S. Stenger
# Date    : 21.06.2021
# Copyright 2021 iSyst Intelligente Systeme GmbH
#
# ******************************************************************************
# ********************************* Version ************************************
# ******************************************************************************
# Rev. | Date       | Name         | Description
# ------------------------------------------------------------------------------
# 1.0  | 21.06.2021 | StengerS     | initial
# 1.1  | 21.12.2021 | H. F?rtsch   | reworked test script by test spec
# ******************************************************************************
#
# Imports #####################################################################
from _automation_wrapper_ import TestEnv
from functions_diag import HexList  # @UnresolvedImport
from diag_identifier import identifier_dict  # @UnresolvedImport

# Instantiate test environment
testenv = TestEnv()

try:
    # #########################################################################
    # Testenv #################################################################
    testenv.setup()
    testresult = testenv.getResults()

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_143")

    # Initialize variables ####################################################
    test_data = identifier_dict['VW Logical Software Block Lock Value']

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] ECU einschalten", ""])
    testenv.startupECU()
    canape_diag = testenv.getCanapeDiagnostic()
    testresult.append(["[.] Tester Present deaktivieren", ""])
    canape_diag.disableTesterPresent()

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

    testresult.append(["\xa0?berpr?fen, dass Request positiv beantwortet wird", ""])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    # test step 2
    testresult.append(["[.] Datenl?nge ?berpr?fen", ""])
    testresult.append(canape_diag.checkDataLength(response, test_data['exp_data_length']))

    # test step 3
    testresult.append(["[.] Sperrwert auf Korrektheit ?berpr?fen", ""])
    expected_response = [0x62] + test_data['identifier'] + test_data['expected_response']
    testresult.append(canape_diag.checkResponse(response, expected_response, ticket_id='Fehler Id:EGA-PRM-24'))

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[.] Test Nachbedingungen", ""])
    testresult.append(["[+] ECU ausschalten", ""])
    testenv.shutdownECU()

finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################