# *****************************************************************************
# -*- coding: latin1 -*-
# File    : Diagnose_Programmzugriffe_94.py
# Title   : Diagnose Programmzugriffe
# Task    : A minimal "Diagnose_Programmzugriffe!" test script
#
# Copyright 2020 Eissmann Automotive Deutschland GmbH
#
# *****************************************************************************
# ******************************** Version ************************************
# *****************************************************************************
# Rev. | Date       | Name     | Description
# -----------------------------------------------------------------------------
# 1.0  | 16.02.2021 | Abdul Karim  | initial
# 1.1  | 28.04.2021 | Abdul Karim  | added Default and Extended Session
# 1.2  | 18.05.2021 | StengerS     | automated test
# 1.3  | 02.12.2021 | H. F�rtsch   | reworked test script by test spec
# *****************************************************************************

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
    testresult.setTestcaseId("TestSpec_94")

    # Initialize variables ####################################################
    test_data = identifier_dict['VW Logical Software Block Counter Of Programming Attempts']

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

    testresult.append(["[.] '{}' auslesen: {}"
                       .format(test_data['name'],
                               HexList(test_data['identifier'])),
                       ""])
    request = [0x22] + test_data['identifier']
    response, result = canape_diag.sendDiagRequest(request)
    testresult.append(result)

    testresult.append(["\xa0�berpr�fen, dass Request positiv beantwortet wird", ""])
    testresult.append(canape_diag.checkPositiveResponse(response, request))

    testresult.append(["[.] Datenl�nge �berpr�fen", ""])
    testresult.append(canape_diag.checkDataLength(response, test_data['exp_data_length']))

    # TEST POST CONDITIONS ####################################################
    testresult.append(["[.] Test Nachbedingungen", ""])
    testresult.append(["[+] ECU ausschalten", ""])
    testenv.shutdownECU()

finally:
    # #########################################################################
    testenv.breakdown()
    del(testenv)
    # #########################################################################

print "Done."
