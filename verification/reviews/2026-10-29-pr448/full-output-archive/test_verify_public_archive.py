import copy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import tarfile
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.parse
import urllib.request

import verify_public_archive as verifier

CASE = 'pr448-hiv-bwa-fixed-a9b588'
WORKFLOW = verifier.EXPECTED_WORKFLOWS[CASE]
LIMIT = 4096
LONG_PATH = 'long/' + 'segment_' * 24 + '/leaf.txt'
PAYLOADS = {'nested/file.txt': b'alpha', LONG_PATH: b'long path contents', 'zero.txt': b''}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tar_bytes(payloads):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode='w|', format=tarfile.PAX_FORMAT) as archive:
        for path, value in sorted(payloads.items()):
            entry = tarfile.TarInfo(path)
            entry.size = len(value)
            archive.addfile(entry, io.BytesIO(value))
    return output.getvalue() + bytes(8192)


def fixture(payloads=PAYLOADS, archive_payloads=None, raw=None):
    raw = raw if raw is not None else tar_bytes(payloads if archive_payloads is None else archive_payloads)
    parts, bodies, names = {}, {}, []
    for index, offset in enumerate(range(0, len(raw), LIMIT), 1):
        name = f'{CASE}-0123456789abcdef.tar.part{index:05d}'
        body = raw[offset:offset + LIMIT]
        names.append(name)
        bodies['/' + name] = body
        parts[name] = dict(case=CASE, state='verified', asset_name=name,
                           release_id=verifier.RELEASE_ID, asset_id=100 + index,
                           bytes=len(body), sha256=sha(body))
    members = [dict(path=name, source_workflow_id=WORKFLOW,
                    original_bytes=len(value), published_bytes=len(value),
                    original_sha256=sha(value), published_sha256=sha(value))
               for name, value in sorted(payloads.items())]
    manifest = dict(repository=verifier.REPO, release_id=verifier.RELEASE_ID,
                    tag=verifier.TAG, parts=parts,
                    cases={CASE: dict(complete=True, parts=names, members=members)},
                    members={CASE + '/' + row['path']: row for row in members})
    release = dict(id=verifier.RELEASE_ID, tag_name=verifier.TAG, draft=False,
                   html_url=f'https://github.com/{verifier.REPO}/releases/tag/{verifier.TAG}',
                   assets=[dict(id=row['asset_id'], name=name, size=row['bytes'], state='uploaded',
                                digest='sha256:' + row['sha256'],
                                browser_download_url=f'https://github.com/{verifier.REPO}/releases/download/{verifier.TAG}/{name}')
                           for name, row in parts.items()])
    bodies['/release.json'] = json.dumps(release).encode()
    return manifest, bodies


class FixtureServer:
    def __init__(self, bodies, overrides=None):
        self.bodies, self.overrides = bodies, overrides or {}
        self.requests = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *args):
                pass

            def do_GET(self):
                owner.requests.append((self.path, dict(self.headers)))
                body = owner.bodies.get(self.path)
                if body is None:
                    self.send_response(404)
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
                config = owner.overrides.get(self.path, {})
                self.send_response(config.get('status', 200))
                for key, value in config.get('headers', {}).items():
                    self.send_header(key, value)
                if 'Content-Length' not in config.get('headers', {}):
                    self.send_header('Content-Length', str(config.get('length', len(body))))
                self.end_headers()
                try:
                    self.wfile.write(body[:config.get('truncate', len(body))])
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                if 'truncate' in config:
                    self.close_connection = True

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


class LocalHTTP:
    """Only tests can substitute the fixed GitHub origins with a loopback fixture."""
    def __init__(self, fixture):
        self.fixture = fixture
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.read_sizes = []

    def open(self, url):
        self_url = '/release.json' if '/releases/' + str(verifier.RELEASE_ID) in url else '/' + url.rsplit('/', 1)[1]
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.fixture.server.server_port}{self_url}',
            headers={'Accept-Encoding': 'identity'}, method='GET')
        response = self.opener.open(request, timeout=2)
        owner = self

        class Tracked:
            status, headers = response.status, response.headers

            def read(self, n):
                owner.read_sizes.append(n)
                return response.read(n)

            def close(self):
                response.close()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()
        return Tracked()


class VerifierTests(unittest.TestCase):
    def execute(self, manifest, bodies, overrides=None, expected_error=None,
                expected_members=None, expected_original_bytes=None, expected_sha=None):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            directory = Path(directory)
            manifest_path, receipt_path = directory / 'manifest.json', directory / 'receipt.json'
            manifest_path.write_text(json.dumps(manifest))
            with FixtureServer(bodies, overrides) as server, patch.object(verifier, 'PART_LIMIT', LIMIT):
                http = LocalHTTP(server)
                kwargs = dict(http=http, workflows={CASE: WORKFLOW},
                              expected_members=len(PAYLOADS) if expected_members is None else expected_members,
                              expected_original_bytes=sum(map(len, PAYLOADS.values())) if expected_original_bytes is None else expected_original_bytes,
                              progress=False, expected_sha=expected_sha)
                if expected_error:
                    with self.assertRaisesRegex(verifier.VerificationError, expected_error):
                        verifier.run(manifest_path, receipt_path, **kwargs)
                    receipt = json.loads(receipt_path.read_text())
                    self.assertEqual(receipt['status'], 'FAILED')
                    self.assertNotIn('https://', receipt.get('failure_code', ''))
                else:
                    receipt = verifier.run(manifest_path, receipt_path, **kwargs)
                    self.assertEqual(receipt, json.loads(receipt_path.read_text()))
                    self.assertEqual(receipt['status'], 'VERIFIED')
                self.assertEqual({p.name for p in directory.iterdir()}, {'manifest.json', 'receipt.json'})
                for _, headers in server.requests:
                    for key in headers:
                        self.assertNotIn(key.lower(), ('authorization', 'cookie', 'proxy-authorization'))
                self.assertTrue(all(0 < n <= verifier.BLOCK for n in http.read_sizes))
                return receipt, server.requests

    def test_real_http_split_tar_pax_paths_zero_byte_member_and_final_padding_parts(self):
        manifest, bodies = fixture()
        receipt, requests = self.execute(manifest, bodies)
        self.assertEqual(receipt['members_verified'], 3)
        self.assertEqual(receipt['cases_verified'], 1)
        self.assertEqual(receipt['parts_verified'], len(manifest['parts']))
        self.assertEqual(receipt['archive_bytes_verified'], sum(row['bytes'] for row in manifest['parts'].values()))
        self.assertEqual(len(requests), len(manifest['parts']) + 1)
        self.assertTrue(receipt['anonymous'])
        self.assertFalse(receipt['payloads_persisted'])
        self.assertIn('manifest_sha256', receipt)
        self.assertIsNotNone(receipt['ended_at'])

    def test_missing_member(self):
        data = dict(PAYLOADS)
        del data[LONG_PATH]
        self.execute(*fixture(archive_payloads=data), expected_error='MISSING_TAR_MEMBER')

    def test_extra_member(self):
        data = dict(PAYLOADS, extra=b'extra')
        self.execute(*fixture(archive_payloads=data), expected_error='UNEXPECTED_OR_DUPLICATE_TAR_MEMBER')

    def test_member_corruption_even_with_consistent_part_hashes(self):
        data = dict(PAYLOADS)
        data['nested/file.txt'] = b'omega'
        self.execute(*fixture(archive_payloads=data), expected_error='TAR_MEMBER_SHA256_MISMATCH')

    def test_member_size_mismatch(self):
        data = dict(PAYLOADS)
        data['nested/file.txt'] = b'longer!'
        self.execute(*fixture(archive_payloads=data), expected_error='TAR_MEMBER_SIZE_MISMATCH')

    def test_final_part_hash_corruption_after_tar_eof(self):
        manifest, bodies = fixture()
        name = list(manifest['parts'])[-1]
        bodies['/' + name] = bodies['/' + name][:-1] + b'X'
        self.execute(manifest, bodies, expected_error='PART_SHA256_MISMATCH|NONZERO_TAR_TRAILER')

    def test_final_part_full_digest_is_verified_after_tar_eof(self):
        manifest, bodies = fixture()
        name = list(manifest['parts'])[-1]
        manifest['parts'][name]['sha256'] = '0' * 64
        release = json.loads(bodies['/release.json'])
        release['assets'][-1]['digest'] = 'sha256:' + '0' * 64
        bodies['/release.json'] = json.dumps(release).encode()
        self.execute(manifest, bodies, expected_error='PART_SHA256_MISMATCH')

    def test_tar_without_end_markers_is_refused(self):
        raw = tar_bytes(PAYLOADS)
        # The deterministic fixture's final member has zero bytes; the last nonzero
        # byte is in that member's header, followed by its header padding.
        end = (len(raw.rstrip(b'\x00')) + 511) // 512 * 512
        self.execute(*fixture(raw=raw[:end]), expected_error='MALFORMED_OR_TRUNCATED_TAR|TAR_END_MARKER_MISSING')

    def test_body_truncation(self):
        manifest, bodies = fixture()
        name = list(manifest['parts'])[-1]
        self.execute(manifest, bodies, {'/' + name: dict(truncate=3)},
                     expected_error='HTTP_PART_TRUNCATED|HTTP_BODY_READ_FAILED')

    def test_protocol_content_length_mismatch(self):
        manifest, bodies = fixture()
        name = next(iter(manifest['parts']))
        self.execute(manifest, bodies, {'/' + name: dict(length=1)},
                     expected_error='HTTP_PART_SIZE_MISMATCH')

    def test_part_order(self):
        manifest, bodies = fixture()
        manifest['cases'][CASE]['parts'].reverse()
        receipt, requests = self.execute(manifest, bodies, expected_error='PART_ORDER_MISMATCH')
        self.assertEqual(requests, [])
        self.assertEqual(receipt['parts_verified'], 0)

    def test_path_validation(self):
        for name in ('../bad', '/absolute', 'nested//bad', 'nested/./bad', 'bad\\path'):
            with self.subTest(path=name):
                manifest, bodies = fixture()
                row = manifest['cases'][CASE]['members'][0]
                old = row['path']
                row['path'] = name
                del manifest['members'][CASE + '/' + old]
                manifest['members'][CASE + '/' + name] = row
                self.execute(manifest, bodies, expected_error='INVALID_PATH')

    def test_empty_tar_is_not_a_zero_member_success(self):
        self.execute(*fixture(archive_payloads={}), expected_error='MISSING_TAR_MEMBER')

    def test_empty_manifest_members_refused(self):
        manifest, bodies = fixture(payloads={})
        self.execute(manifest, bodies, expected_members=0, expected_original_bytes=0,
                     expected_error='EMPTY_CASE_MEMBERS')

    def test_incomplete_case_refused_before_http(self):
        manifest, bodies = fixture()
        manifest['cases'][CASE]['complete'] = False
        _, requests = self.execute(manifest, bodies, expected_error='CASE_INCOMPLETE')
        self.assertEqual(requests, [])

    def test_public_release_identity_and_publication_required(self):
        for changes in ({'draft': True}, {'id': 1}, {'tag_name': 'wrong'}):
            with self.subTest(changes=changes):
                manifest, bodies = fixture()
                release = json.loads(bodies['/release.json'])
                release.update(changes)
                bodies['/release.json'] = json.dumps(release).encode()
                self.execute(manifest, bodies, expected_error='PUBLIC_RELEASE_IDENTITY_MISMATCH')

    def test_no_sensitive_exception_text_is_persisted(self):
        manifest, bodies = fixture()
        with patch.object(LocalHTTP, 'open', side_effect=OSError('https://host/?signed_token=not-a-real-secret')):
            receipt, _ = self.execute(manifest, bodies, expected_error='UNEXPECTED_VERIFICATION_ERROR')
        self.assertNotIn('signed_token', json.dumps(receipt))

    def test_wrong_manifest_pin_refused(self):
        self.execute(*fixture(), expected_sha='0' * 64, expected_error='MANIFEST_SHA256_MISMATCH')

    def test_expected_totals_and_workflow_are_required(self):
        self.execute(*fixture(), expected_members=4, expected_error='MEMBER_COUNT_MISMATCH')
        self.execute(*fixture(), expected_original_bytes=1, expected_error='ORIGINAL_BYTE_COUNT_MISMATCH')
        manifest, bodies = fixture()
        manifest['cases'][CASE]['members'][0]['source_workflow_id'] = 'different'
        self.execute(manifest, bodies, expected_error='SOURCE_WORKFLOW_MISMATCH')

    def test_duplicate_json_keys_refused(self):
        with self.assertRaisesRegex(verifier.VerificationError, 'DUPLICATE_JSON_KEY'):
            verifier.parse_json(b'{"a":1,"a":2}')

    def test_nonregular_tar_member_refused(self):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w', format=tarfile.PAX_FORMAT) as archive:
            entry = tarfile.TarInfo('directory')
            entry.type = tarfile.DIRTYPE
            archive.addfile(entry)
        self.execute(*fixture(raw=output.getvalue()), expected_error='UNSUPPORTED_TAR_MEMBER_TYPE')

    def test_anonymous_transport_has_no_environment_proxy_or_auth_handlers(self):
        http = verifier.AnonymousHTTP()
        names = {type(handler).__name__ for handler in http.opener.handlers}
        self.assertFalse(any('Auth' in name or 'Cookie' in name for name in names))
        self.assertNotIn('ProxyHandler', names)
        self.assertTrue(verifier.allowed_https('https://release-assets.githubusercontent.com/a?opaque=memory-only'))
        self.assertFalse(verifier.allowed_https('http://github.com/a'))


if __name__ == '__main__':
    unittest.main()
