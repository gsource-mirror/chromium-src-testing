# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Enforces json format.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts
for more details on the presubmit API built into depot_tools.
"""

_IGNORE_FREEZE_FOOTER = 'Ignore-Freeze'

# The time module's handling of timezones is abysmal, so the boundaries are
# precomputed in UNIX time
_FREEZE_START = 1639641600  # 2021/12/16 00:00 -0800
_FREEZE_END = 1641196800  # 2022/01/03 00:00 -0800


def CheckFreeze(input_api, output_api):
  if _FREEZE_START <= input_api.time.time() < _FREEZE_END:
    footers = input_api.change.GitFootersFromDescription()
    if _IGNORE_FREEZE_FOOTER not in footers:

      def convert(t):
        ts = input_api.time.localtime(t)
        return input_api.time.strftime('%Y/%m/%d %H:%M %z', ts)

      return [
          output_api.PresubmitError(
              'There is a prod freeze in effect from {} until {},'
              ' files in //testing/buildbot cannot be modified'.format(
                  convert(_FREEZE_START), convert(_FREEZE_END)))
      ]

  return []


def CommonChecks(input_api, output_api):
  commands = [
    input_api.Command(
      name='generate_buildbot_json', cmd=[
        input_api.python_executable, 'generate_buildbot_json.py', '--check',
        '--verbose'],
      kwargs={}, message=output_api.PresubmitError),

    input_api.Command(
      name='generate_buildbot_json_unittest', cmd=[
        input_api.python_executable, 'generate_buildbot_json_unittest.py'],
      kwargs={}, message=output_api.PresubmitError),

    input_api.Command(
      name='generate_buildbot_json_coveragetest', cmd=[
        input_api.python_executable, 'generate_buildbot_json_coveragetest.py'],
      kwargs={}, message=output_api.PresubmitError),

    input_api.Command(
      name='buildbot_json_magic_substitutions_unittest', cmd=[
        input_api.python_executable,
        'buildbot_json_magic_substitutions_unittest.py',
      ], kwargs={}, message=output_api.PresubmitError
    ),

    input_api.Command(
      name='manage', cmd=[
        input_api.python_executable, 'manage.py', '--check'],
      kwargs={}, message=output_api.PresubmitError),
  ]
  messages = []

  messages.extend(input_api.RunTests(commands))
  messages.extend(CheckFreeze(input_api, output_api))
  return messages


def CheckChangeOnUpload(input_api, output_api):
  return CommonChecks(input_api, output_api)


def CheckChangeOnCommit(input_api, output_api):
  return CommonChecks(input_api, output_api)
