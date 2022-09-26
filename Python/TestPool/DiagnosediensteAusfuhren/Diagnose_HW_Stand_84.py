# *****************************************************************************
# -*- coding: latin1 -*-
# File    : Diagnose_HW_Stand_84.py
# Title   : Diagnose HW Stand
# Task    : A minimal "Diagnose_HW_Stand!" test script
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
# 1.3  | 28.05.2021 | StengerS     | read out HW version from iTestStudio
# 1.4  | 31.05.2021 | StengerS     | added info for not implemented jobs
# 1.5  | 06.09.2021 | Mohammed     | changed info SW name to HW
# 1.6  | 02.12.2021 | H. F�rtsch   | reworked test script by test spec
# *****************************************************************************

# Imports #####################################################################
from _automation_wrapper_ import TestEnv
from functions_diag import HexList, calcVersionString
from diag_identifier import identifier_dict  # @UnresolvedImport

# Instantiate test environment
testenv = TestEnv()

try:
    # #########################################################################
    # Testenv #################################################################
    testenv.setup()
    testresult = testenv.getResults()

    # set Testcase ID #########################################################
    testresult.setTestcaseId("TestSpec_84")

    # Initialize functions ####################################################

    # Initialize variables ####################################################
    test_list = [identifier_dict['ECU Serial Number'],
                 identifier_dict['System Supplier ECU Hardware Number'],
                 identifier_dict['System Supplier ECU Hardware Version Number'],
                 identifier_dict['VW ECU Hardware Version Number']]

    # TEST PRE CONDITIONS #####################################################
    testresult.append(["[#0] Test Vorbedingungen", ""])
    testresult.append(["[+] ECU einschalten", ""])
    testenv.startupECU()
    canape_diag = testenv.getCanapeDiagnostic()
    testresult.append(["[.] Tester Present deaktivieren", ""])
    canape_diag.disableTesterPresent()

    # TEST PROCESS ############################################################
    testresult.append(["\n Starte Testprozess: {}".format(testenv.script_name.split('.py')[0]), ""])
    # silently go one chapter level up, add next parent chapter
    testresult.append(["[-0]", ""])

    for test_data in test_list:
        testresult.append(["[.] {}".format(test_data['name']), ""])

        testresult.append(["[+] '{}' auslesen: {}"
                           .format(test_data['name'],
                                   HexList(test_data['identifier'])),
                           ""])
        request = [0x22] + test_data['identifier']
        [response, result] = canape_diag.sendDiagRequest(request)
        testresult.append(result)

        testresult.append(["\xa0�berpr�fen, dass Request positiv beantwortet wird", ""])
        testresult.append(canape_diag.checkPositiveResponse(response, request))

        testresult.append(["[.] Datenl�nge �berpr�fen", ""])
        testresult.append(canape_diag.checkDataLength(response, test_data['exp_data_length']))

        testresult.append(["[.] Inhalt auf Korrektheit �berpr�fen", ""])
        if test_data['name'] == 'VW ECU Hardware Version Number':

            # H. F�rtsch (2021-12-02): commented out, because not part of test spec
            # try:
            #     hw_version = ''.join(chr(i) for i in response[3:])
            # except:
            #     testresult.append(["Response cannot be decoded (ASCII): %s" % response, "FAILED"])
            #
            # current_series = os.getenv("ITESTSTUDIO_CURRENT_SER", None)
            # if current_series:
            #     exp_hw_version = func_common.getVersionFromiTestStudio(current_series, 'HARDWAREVERSION')
            #     testresult.append(["Read version from %s: %s" % (current_series, str(exp_hw_version)), ""])
            #
            #     if hw_version == exp_hw_version:
            #         descr = ("The version read out is the same as that from the test series\n"
            #                 "Read out HW version: %s\n"
            #                 "HW Version from test series: %s" %(str(hw_version), str(exp_hw_version)))
            #         verdict = "PASSED"
            #     else:
            #         descr = ("The version read out does NOT match the version from the test series\n"
            #                 "Read out HW version: %s\n"
            #                 "HW Version from test series: %s" %(str(hw_version), str(exp_hw_version)))
            #         verdict = "FAILED"
            #
            # else:
            #     exp_hw_version = test_data['expected_response']
            #     exp_hw_version = ''.join(chr(i) for i in exp_hw_version)
            hw_version = response[3:]
            exp_hw_version = test_data['expected_response']

            if hw_version == exp_hw_version:
                descr = "The version read out is as expected\n"
                verdict = "PASSED"
            else:
                descr = "The version read out is NOT as expected\n"
                verdict = "FAILED"
            descr += ("Read out HW version: {}\n"
                      "HW Version from diag_identifier: {}") \
                     .format(calcVersionString(hw_version), calcVersionString(exp_hw_version))

            testresult.append([descr, verdict])

        else:
            expected_response = [0x62] + test_data['identifier'] + test_data['expected_response']
            testresult.append(canape_diag.checkResponse(response, expected_response))

        # silently go one chapter level up
        testresult.append(["[-0]", ""])

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
