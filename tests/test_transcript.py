import gzip
import contextlib
import io
import importlib.machinery
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/codex-session-scout/scripts/codex-session-scout'
loader = importlib.machinery.SourceFileLoader('scout', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
scout = importlib.util.module_from_spec(spec)
loader.exec_module(scout)


def event(event_type, **kw):
    return {'type': 'event_msg', 'payload': {'type': event_type, **kw}}


def user(id, turn, text):
    return event('item_completed', turn_id=turn, item={'type': 'UserMessage', 'id': id,
                 'content': [{'type': 'text', 'text': text}, {'type': 'image'}]})


def final(turn, text):
    return {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
            'phase': 'final_answer', 'id': 'final-'+turn, 'content': [{'type': 'output_text', 'text': text}],
            'internal_chat_message_metadata_passthrough': {'turn_id': turn}}}


class TranscriptTests(unittest.TestCase):
    def run_events(self, events, suffix='.jsonl'):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ('test' + suffix)
            data = ''.join(e if isinstance(e, str) else json.dumps(e) + '\n' for e in events)
            if suffix.endswith('.gz'):
                with gzip.open(path, 'wt') as f: f.write(data)
            else:
                path.write_text(data)
            return scout.transcript(path)

    def test_turns_steering_duplicates_and_interruption(self):
        events = [event('task_started', turn_id='a'), user('u1', 'a', 'first'),
                  {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'phase': 'commentary', 'content': [{'text': 'ignore'}]}},
                  user('u2', 'a', 'steering'), final('a', 'shared'), event('task_complete', turn_id='a'),
                  event('task_started', turn_id='b'), user('u3', 'b', 'next'), final('b', 'done'), event('task_complete', turn_id='b'),
                  event('task_started', turn_id='c'), user('u4', 'c', 'unfinished'), event('turn_aborted', turn_id='c'),
                  event('task_started', turn_id='d'), user('u5', 'd', 'no final')]
        records, errors = self.run_events(events)
        self.assertEqual(errors, 0)
        self.assertEqual([r['association'] for r in records], ['ambiguous_shared_turn', 'ambiguous_shared_turn', 'matched', 'interrupted', 'no_final'])
        self.assertEqual(records[0]['final_answers'][0]['text'], 'shared')
        self.assertEqual(records[2]['final_answers'][0]['text'], 'done')

    def test_duplicate_response_and_ambient_ignored(self):
        metadata = {'turn_id': 't', 'content_item_metadata': [{'provenance': {'type': 'user'}}]}
        response = {'type': 'response_item', 'payload': {'type': 'message', 'role': 'user', 'id': 'response',
                    'content': [{'text': 'same'}], 'internal_chat_message_metadata_passthrough': metadata}}
        ambient = {'type': 'response_item', 'payload': {'type': 'message', 'role': 'user', 'content': [{'text': 'ambient'}]}}
        records, _ = self.run_events([event('task_started', turn_id='t'), ambient, response, user('item', 't', 'same'), final('t', 'ok')])
        self.assertEqual([(x['id'], x['text']) for x in records], [('item', 'same')])

    def test_legacy_malformed_gzip_and_completion_fallback(self):
        records, errors = self.run_events([event('task_started', turn_id='x'), '{bad\n', event('user_message', message='hello'),
                                           event('task_complete', turn_id='x', last_agent_message='ok')], '.jsonl.gz')
        self.assertEqual(errors, 1)
        self.assertEqual(records[0]['id'], 'line:3')
        self.assertEqual(records[0]['final_answers'][0]['text'], 'ok')
        self.assertEqual(records[0]['association'], 'matched')

    @unittest.skipUnless(shutil.which('zstd'), 'zstd not installed')
    def test_zstd_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'test.jsonl.zst'
            data = (json.dumps(user('u', 't', 'hello')) + '\n' + json.dumps(final('t', 'ok')) + '\n').encode()
            path.write_bytes(subprocess.run(['zstd', '-q', '-c'], input=data, capture_output=True, check=True).stdout)
            self.assertEqual(scout.transcript(path)[0][0]['association'], 'matched')
            path.write_bytes(b'not a zstd stream')
            with self.assertRaises(OSError):
                scout.transcript(path)

    def test_no_turn_is_never_matched(self):
        records, _ = self.run_events([event('user_message', message='hello')])
        self.assertEqual(records[0]['association'], 'unknown_turn')

    def test_cli_select_and_missing_id(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'events.jsonl'
            path.write_text(''.join(json.dumps(x) + '\n' for x in [user('u', 't', 'hi'), final('t', 'ok')]))
            with mock.patch.object(scout, 'find_session_by_id', return_value=path):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    args = scout.build_parser().parse_args(['transcript', 'session', '--message', 'u', '--format', 'json'])
                    self.assertEqual(args.func(args), 0)
                    self.assertEqual(json.loads(out.getvalue())[0]['final_answers'][0]['text'], 'ok')
                    args = scout.build_parser().parse_args(['transcript', 'session', '--message', 'missing'])
                    self.assertEqual(args.func(args), 2)
                    self.assertIn('not found', err.getvalue())

    def test_multiple_finals_are_ambiguous(self):
        records, _ = self.run_events([user('u', 't', 'hello'), final('t', 'a'), final('t', 'b')])
        self.assertEqual(records[0]['association'], 'ambiguous_shared_turn')


if __name__ == '__main__':
    unittest.main()
