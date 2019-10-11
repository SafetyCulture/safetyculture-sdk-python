import os
import sys

import unittest
import mock
from mock import patch

sys.path.append(os.path.join(os.getcwd(), '..', '..', 'exporter'))
import exporter as exp

class ExporterLoggingTestCase(unittest.TestCase):

    def test_log_critical_error_logs_message_and_exception_if_logger_is_not_none(self):
        mock_logger = mock.Mock()
        ex = ArithmeticError
        msg = "Some Arithmetic Error"

        exp.log_critical_error(mock_logger, ex, msg)

        mock_logger.critical.assert_any_call(ex)
        mock_logger.critical.assert_any_call(msg)

    def test_log_critical_error_when_logger_is_none(self):
        exp.log_critical_error(None, None, None)

    @patch('exporter.configure_logging')
    @patch('exporter.create_directory_if_not_exists')
    @patch('exporter.logging')
    @patch('exporter.os')
    def test_configure_logger_calls_with_proper_string_and_returns_logger(self, mock_os, mock_logging, mock_create, mock_config):
        mock_logging.getLogger.side_effect = 'x'

        test_logger = exp.configure_logger()

        mock_logging.getLogger.assert_called_with('exporter_logger')
        self.assertEqual(test_logger, 'x')

    @patch('exporter.configure_logging')
    @patch('exporter.create_directory_if_not_exists')
    @patch('exporter.logging')
    @patch('exporter.os')
    def test_configure_logger_creates_proper_directory(self, mock_os, mock_logging, mock_create, mock_config):
        def returns_dir(arg1, arg2):
            return "dir"
        mock_os.path.join.side_effect = returns_dir

        test_logger = exp.configure_logger()

        mock_create.assert_called_with(None, "dir")
        mock_config.assert_called_with("dir")

    @patch('exporter.sys')
    @patch('exporter.datetime')
    @patch('exporter.logging')
    def test_configure_logging(self, mock_logging, mock_datetime, mock_sys):
        mock_logger = mock.Mock()
        def returns_mock_logger(name):
            mock_logger.called_name = name
            return mock_logger
        mock_logging.getLogger.side_effect = returns_mock_logger
        mock_logging.Formatter.side_effect = 'f'

        mock_file_handler = mock.Mock()
        def returns_mock_file_handler(filename):
            mock_file_handler.file_path = filename
            return mock_file_handler
        mock_logging.FileHandler.side_effect = returns_mock_file_handler

        mock_stream_handler = mock.Mock()
        def returns_mock_stream_handler(stream):
            mock_stream_handler.stream = stream
            return mock_stream_handler
        mock_logging.StreamHandler.side_effect = returns_mock_stream_handler

        mock_now = mock.Mock()
        mock_now.strftime.side_effect = 't'
        def returns_mock_now():
            return mock_now
        mock_datetime.now.side_effect = returns_mock_now

        mock_sys.stdout = 's'

        exp.configure_logging('somepath')
        mock_now.strftime.assert_called_with('%Y-%m-%d')
        mock_logging.getLogger.assert_called_with('exporter_logger')
        self.assertEqual(mock_logger.called_name, 'exporter_logger')
        mock_logger.setLevel.assert_any_call(exp.LOG_LEVEL)

        mock_logging.Formatter.assert_called_with('%(asctime)s : %(levelname)s : %(message)s')

        mock_logging.FileHandler.assert_called_with(filename=os.path.join('somepath', 't.log'))
        mock_file_handler.setLevel.assert_called_with(exp.LOG_LEVEL)
        mock_file_handler.setFormatter.assert_called_with('f')
        mock_logger.addHandler.assert_any_call(mock_file_handler)

        mock_logging.StreamHandler.assert_called_with('s')
        mock_stream_handler.setLevel.assert_called_with(exp.LOG_LEVEL)
        mock_stream_handler.setFormatter.assert_called_with('f')
        mock_logger.addHandler.assert_any_call(mock_stream_handler)


if __name__ == '__main__':
    unittest.main()
