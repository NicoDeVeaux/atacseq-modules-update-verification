#!/usr/bin/env python3
"""Verify the pinned public PR448 archive anonymously, without payload persistence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request

REPO = 'NicoDeVeaux/atacseq-modules-update-verification'
RELEASE_ID = 427625994
TAG = 'pr448-full-repro-2026-10-29'
EXPECTED_WORKFLOWS = {
    'pr448-hiv-bwa-fixed-a9b588': 'BVYqNpYNcUhEN',
    'pr448-hiv-bwa-unfixed-a9b588': 'miH78tIWtzQMy',
    'pr448-hiv-chromap-fixed-a9b588': '2DOXAsX9V2FbkY',
    'pr448-hiv-chromap-unfixed-a9b588': '6n2TeKZ3HxTua',
}
EXPECTED_MEMBERS = 2686
EXPECTED_ORIGINAL_BYTES = 43838229376
BLOCK = 1024 * 1024
MAX_MANIFEST_BYTES = 32 * BLOCK
MAX_METADATA_BYTES = 2 * BLOCK
MAX_PAX_BYTES = 64 * 1024
PART_LIMIT = 1536 * BLOCK
HEX64 = re.compile(r'[0-9a-f]{64}\Z')


class VerificationError(Exception):
    pass


def require(condition, code):
    if not condition:
        raise VerificationError(code)


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def safe_path(value):
    require(isinstance(value, str) and bool(value), 'INVALID_PATH')
    require(not value.startswith('/') and '\\' not in value and ':' not in value,
            'INVALID_PATH')
    require(not re.search(r'%[0-9a-fA-F]{2}', value), 'INVALID_PATH')
    require(not any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF
                    for c in value), 'INVALID_PATH')
    require(not any(p in ('', '.', '..') for p in value.split('/')), 'INVALID_PATH')
    return value


def integer(value, code, minimum=0):
    require(type(value) is int and value >= minimum, code)
    return value


def no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'DUPLICATE_JSON_KEY')
        obj[key] = value
    return obj


def parse_json(raw):
    try:
        return json.loads(raw, object_pairs_hook=no_duplicates)
    except VerificationError:
        raise
    except (UnicodeError, ValueError, TypeError):
        raise VerificationError('INVALID_JSON') from None


def validate_manifest(manifest, workflows=EXPECTED_WORKFLOWS,
                      expected_members=EXPECTED_MEMBERS,
                      expected_original_bytes=EXPECTED_ORIGINAL_BYTES):
    require(isinstance(manifest, dict), 'INVALID_MANIFEST')
    require(manifest.get('repository') == REPO and
            manifest.get('release_id') == RELEASE_ID and
            manifest.get('tag') == TAG, 'ARCHIVE_IDENTITY_MISMATCH')
    cases, parts, flat_members = (manifest.get(k) for k in ('cases', 'parts', 'members'))
    require(isinstance(cases, dict) and set(cases) == set(workflows),
            'CASE_INVENTORY_MISMATCH')
    require(isinstance(parts, dict) and bool(parts), 'INVALID_PART_INVENTORY')
    require(isinstance(flat_members, dict), 'INVALID_MEMBER_INVENTORY')
    used_parts, canonical_members = set(), {}
    total_members = total_original = total_published = 0
    result = []
    for name in sorted(cases):
        safe_path(name)
        record = cases[name]
        require(isinstance(record, dict) and record.get('complete') is True,
                'CASE_INCOMPLETE')
        ordered, members = record.get('parts'), record.get('members')
        require(isinstance(ordered, list) and bool(ordered), 'EMPTY_CASE_PARTS')
        require(isinstance(members, list) and bool(members), 'EMPTY_CASE_MEMBERS')
        expected, prefix = {}, None
        for index, part in enumerate(ordered, 1):
            safe_path(part)
            require('/' not in part, 'INVALID_PART_NAME')
            match = re.fullmatch(re.escape(name) + r'-([0-9a-f]{16})\.tar\.part(\d{5})', part)
            require(match is not None and int(match[2]) == index, 'PART_ORDER_MISMATCH')
            prefix = prefix or match[1]
            require(match[1] == prefix and part not in used_parts, 'PART_IDENTITY_MISMATCH')
            used_parts.add(part)
            item = parts.get(part)
            require(isinstance(item, dict) and item.get('case') == name and
                    item.get('state') == 'verified' and item.get('asset_name') == part and
                    item.get('release_id') == RELEASE_ID, 'PART_IDENTITY_MISMATCH')
            require(HEX64.fullmatch(item.get('sha256', '')) is not None, 'INVALID_PART_SHA256')
            integer(item.get('asset_id'), 'INVALID_ASSET_ID', 1)
            size = integer(item.get('bytes'), 'INVALID_PART_SIZE', 1)
            require(size <= PART_LIMIT, 'PART_SIZE_LIMIT')
            if index < len(ordered):
                require(size == PART_LIMIT, 'NONFINAL_PART_SIZE_MISMATCH')
        for row in members:
            require(isinstance(row, dict), 'INVALID_MEMBER')
            path = safe_path(row.get('path'))
            require(path not in expected, 'DUPLICATE_MEMBER')
            require(row.get('source_workflow_id') == workflows[name], 'SOURCE_WORKFLOW_MISMATCH')
            for key in ('original_sha256', 'published_sha256'):
                require(HEX64.fullmatch(row.get(key, '')) is not None, 'INVALID_MEMBER_SHA256')
            total_original += integer(row.get('original_bytes'), 'INVALID_MEMBER_SIZE')
            total_published += integer(row.get('published_bytes'), 'INVALID_MEMBER_SIZE')
            expected[path] = row
            canonical_members[name + '/' + path] = row
        total_members += len(expected)
        result.append((name, ordered, expected))
    require(used_parts == set(parts), 'UNREFERENCED_OR_MISSING_PART')
    require(flat_members == canonical_members, 'FLAT_MEMBER_INVENTORY_MISMATCH')
    require(total_members == expected_members and total_members > 0, 'MEMBER_COUNT_MISMATCH')
    require(total_original == expected_original_bytes, 'ORIGINAL_BYTE_COUNT_MISMATCH')
    return result, total_published


def allowed_https(url):
    try:
        parsed = urllib.parse.urlsplit(url)
        return (parsed.scheme == 'https' and parsed.username is None and
                parsed.password is None and parsed.port in (None, 443) and
                parsed.hostname in {'api.github.com', 'github.com',
                                    'release-assets.githubusercontent.com',
                                    'objects.githubusercontent.com'})
    except ValueError:
        return False


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require(allowed_https(newurl), 'REDIRECT_DESTINATION_REFUSED')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class AnonymousHTTP:
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), PublicRedirect())

    def open(self, url):
        require(allowed_https(url), 'REQUEST_DESTINATION_REFUSED')
        request = urllib.request.Request(url, headers={
            'Accept': 'application/octet-stream', 'Accept-Encoding': 'identity',
            'User-Agent': 'PR448-anonymous-readonly-archive-verifier/1',
        }, method='GET')
        try:
            return self.opener.open(request, timeout=self.timeout)
        except VerificationError:
            raise
        except (urllib.error.URLError, OSError, http.client.HTTPException):
            raise VerificationError('ANONYMOUS_HTTP_GET_FAILED') from None


def response_headers(response, expected_size=None):
    require(response.status == 200, 'HTTP_STATUS_MISMATCH')
    encoding = response.headers.get('Content-Encoding')
    require(encoding is None or encoding.lower() == 'identity', 'HTTP_ENCODING_REFUSED')
    require(response.headers.get('Content-Range') is None, 'UNEXPECTED_CONTENT_RANGE')
    if expected_size is not None:
        require(response.headers.get('Transfer-Encoding') is None, 'TRANSFER_ENCODING_REFUSED')
        lengths = response.headers.get_all('Content-Length')
        require(lengths is not None and len(lengths) == 1 and
                re.fullmatch(r'[0-9]+', lengths[0]) is not None, 'CONTENT_LENGTH_REQUIRED')
        require(int(lengths[0]) == expected_size, 'HTTP_PART_SIZE_MISMATCH')


def read_response(response, n):
    require(0 < n <= BLOCK, 'UNBOUNDED_READ_REFUSED')
    try:
        data = response.read(n)
    except (OSError, EOFError, http.client.HTTPException):
        raise VerificationError('HTTP_BODY_READ_FAILED') from None
    require(isinstance(data, bytes) and len(data) <= n, 'HTTP_READ_PROTOCOL_MISMATCH')
    return data


def verify_public_release(http, manifest):
    url = f'https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}'
    with http.open(url) as response:
        response_headers(response)
        chunks, size = [], 0
        while True:
            chunk = read_response(response, min(BLOCK, MAX_METADATA_BYTES + 1 - size))
            if not chunk:
                break
            size += len(chunk)
            require(size <= MAX_METADATA_BYTES, 'RELEASE_METADATA_SIZE_LIMIT')
            chunks.append(chunk)
    release = parse_json(b''.join(chunks))
    require(isinstance(release, dict) and release.get('id') == RELEASE_ID and
            release.get('tag_name') == TAG and release.get('draft') is False and
            release.get('html_url') == f'https://github.com/{REPO}/releases/tag/{TAG}',
            'PUBLIC_RELEASE_IDENTITY_MISMATCH')
    assets = release.get('assets')
    require(isinstance(assets, list), 'INVALID_RELEASE_ASSETS')
    by_name = {}
    for item in assets:
        require(isinstance(item, dict), 'INVALID_RELEASE_ASSET')
        name = item.get('name')
        require(isinstance(name, str) and name not in by_name, 'DUPLICATE_RELEASE_ASSET')
        by_name[name] = item
    for name, expected in manifest['parts'].items():
        asset = by_name.get(name)
        require(isinstance(asset, dict) and asset.get('id') == expected['asset_id'] and
                asset.get('size') == expected['bytes'] and asset.get('state') == 'uploaded' and
                asset.get('browser_download_url') ==
                f'https://github.com/{REPO}/releases/download/{TAG}/{name}',
                'PUBLIC_ASSET_IDENTITY_MISMATCH')
        digest = asset.get('digest')
        require(digest is None or digest == 'sha256:' + expected['sha256'],
                'PUBLIC_ASSET_DIGEST_MISMATCH')


class JoinedParts:
    """Expose bounded reads and verify each HTTP response before advancing."""
    def __init__(self, names, parts, http, on_part):
        self.names, self.parts = iter(names), parts
        self.http, self.on_part = http, on_part
        self.current, self.done, self.total = None, False, 0

    def _begin(self):
        try:
            self.name = next(self.names)
        except StopIteration:
            self.done = True
            return
        self.row = self.parts[self.name]
        url = f'https://github.com/{REPO}/releases/download/{TAG}/{self.name}'
        self.current = self.http.open(url)
        response_headers(self.current, self.row['bytes'])
        self.left, self.digest = self.row['bytes'], hashlib.sha256()

    def _finish(self):
        require(read_response(self.current, 1) == b'', 'HTTP_PART_EXTRA_BYTES')
        require(self.digest.hexdigest() == self.row['sha256'], 'PART_SHA256_MISMATCH')
        self.current.close()
        self.current = None
        self.on_part(self.name, self.row)

    def read(self, n):
        require(type(n) is int and 0 <= n <= BLOCK, 'UNBOUNDED_READ_REFUSED')
        chunks, left = [], n
        while left and not self.done:
            if self.current is None:
                self._begin()
                if self.done:
                    break
            if self.left == 0:
                self._finish()
                continue
            chunk = read_response(self.current, min(left, self.left))
            require(bool(chunk), 'HTTP_PART_TRUNCATED')
            self.left -= len(chunk)
            left -= len(chunk)
            self.total += len(chunk)
            self.digest.update(chunk)
            chunks.append(chunk)
        return b''.join(chunks)

    def close(self):
        if self.current is not None:
            self.current.close()
            self.current = None


class BoundedTarInfo(tarfile.TarInfo):
    @classmethod
    def fromtarfile(cls, archive):
        try:
            return super().fromtarfile(archive)
        except tarfile.EOFHeaderError:
            archive._pr448_zero_end_marker = True
            raise
        except (tarfile.InvalidHeaderError, tarfile.EmptyHeaderError,
                tarfile.TruncatedHeaderError):
            raise VerificationError('MALFORMED_OR_TRUNCATED_TAR') from None

    def _proc_member(self, archive):
        require(self.type in (tarfile.REGTYPE, tarfile.AREGTYPE, tarfile.XHDTYPE),
                'UNSUPPORTED_TAR_MEMBER_TYPE')
        return super()._proc_member(archive)

    def _proc_pax(self, archive):
        require(0 < self.size <= MAX_PAX_BYTES, 'PAX_METADATA_LIMIT')
        depth = getattr(archive, '_pr448_pax_depth', 0)
        require(depth < 4, 'PAX_METADATA_DEPTH_LIMIT')
        archive._pr448_pax_depth = depth + 1
        try:
            return super()._proc_pax(archive)
        finally:
            archive._pr448_pax_depth = depth

    def _proc_gnusparse_00(self, *args):
        raise VerificationError('SPARSE_TAR_REFUSED')

    _proc_gnusparse_01 = _proc_gnusparse_00
    _proc_gnusparse_10 = _proc_gnusparse_00


def verify_tar(joined, expected):
    seen, published = set(), 0
    try:
        with tarfile.open(fileobj=joined, mode='r|', bufsize=64 * 1024,
                          tarinfo=BoundedTarInfo) as archive:
            for entry in archive:
                path = safe_path(entry.name)
                require(entry.isfile() and entry.sparse is None and
                        path in expected and path not in seen,
                        'UNEXPECTED_OR_DUPLICATE_TAR_MEMBER')
                row = expected[path]
                require(entry.size == row['published_bytes'], 'TAR_MEMBER_SIZE_MISMATCH')
                digest, size = hashlib.sha256(), 0
                member = archive.extractfile(entry)
                require(member is not None, 'TAR_MEMBER_UNREADABLE')
                with member:
                    while True:
                        chunk = member.read(BLOCK)
                        if not chunk:
                            break
                        digest.update(chunk)
                        size += len(chunk)
                require(size == entry.size, 'TAR_MEMBER_TRUNCATED')
                require(digest.hexdigest() == row['published_sha256'],
                        'TAR_MEMBER_SHA256_MISMATCH')
                seen.add(path)
                published += size
            require(seen == set(expected) and bool(seen), 'MISSING_TAR_MEMBER')
            # Require both TAR end blocks; tarfile otherwise accepts EOF or malformed later headers.
            require(getattr(archive, '_pr448_zero_end_marker', False), 'TAR_END_MARKER_MISSING')
            require(archive.fileobj.read(512) == bytes(512), 'TAR_END_MARKER_MISSING')
            # Drain tarfile's buffered bytes, then the source, including all final-part padding.
            while True:
                chunk = archive.fileobj.read(BLOCK)
                if not chunk:
                    break
                require(not chunk.strip(b'\x00'), 'NONZERO_TAR_TRAILER')
        while True:
            chunk = joined.read(BLOCK)
            if not chunk:
                break
            require(not chunk.strip(b'\x00'), 'NONZERO_TAR_TRAILER')
    except VerificationError:
        raise
    except (tarfile.TarError, OSError, EOFError, UnicodeError, ValueError):
        raise VerificationError('MALFORMED_OR_TRUNCATED_TAR') from None
    return len(seen), published


def save_receipt(path, receipt):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'w') as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def run(manifest_path, receipt_path, expected_sha=None, http=None,
        workflows=EXPECTED_WORKFLOWS, expected_members=EXPECTED_MEMBERS,
        expected_original_bytes=EXPECTED_ORIGINAL_BYTES, progress=True):
    receipt = {
        'schema': 'pr448/anonymous-public-stream-verification/v1',
        'repository': REPO, 'release_id': RELEASE_ID, 'tag': TAG,
        'status': 'VERIFYING', 'started_at': utcnow(), 'ended_at': None,
        'anonymous': True, 'remote_writes': False, 'payloads_persisted': False,
        'cases_verified': 0, 'parts_verified': 0, 'members_verified': 0,
        'archive_bytes_verified': 0, 'published_member_bytes_verified': 0,
        'original_member_bytes': expected_original_bytes,
        'max_io_read_bytes': BLOCK, 'parts': [], 'cases': [],
    }
    try:
        with Path(manifest_path).open('rb') as handle:
            raw = handle.read(MAX_MANIFEST_BYTES + 1)
        require(len(raw) <= MAX_MANIFEST_BYTES, 'MANIFEST_SIZE_LIMIT')
        digest = hashlib.sha256(raw).hexdigest()
        receipt['manifest_sha256'] = digest
        if expected_sha is not None:
            require(HEX64.fullmatch(expected_sha) is not None and expected_sha == digest,
                    'MANIFEST_SHA256_MISMATCH')
        manifest = parse_json(raw)
        cases, published_bytes = validate_manifest(manifest, workflows, expected_members,
                                                   expected_original_bytes)
        receipt.update(expected_cases=len(cases), expected_parts=len(manifest['parts']),
                       expected_members=expected_members)
        save_receipt(receipt_path, receipt)
        http = http or AnonymousHTTP()
        verify_public_release(http, manifest)
        receipt['public_release_identity_verified'] = True
        save_receipt(receipt_path, receipt)

        def part_verified(name, row):
            receipt['parts'].append({'name': name, 'bytes': row['bytes'],
                                     'sha256': row['sha256'], 'verified_at': utcnow()})
            receipt['parts_verified'] += 1
            receipt['archive_bytes_verified'] += row['bytes']
            save_receipt(receipt_path, receipt)
            if progress:
                print(f'part {receipt["parts_verified"]}/{receipt["expected_parts"]} verified', flush=True)

        for name, names, expected in cases:
            joined = JoinedParts(names, manifest['parts'], http, part_verified)
            try:
                members, size = verify_tar(joined, expected)
            finally:
                joined.close()
            receipt['cases'].append({'case': name, 'members': members,
                                     'published_bytes': size, 'parts': len(names)})
            receipt['cases_verified'] += 1
            receipt['members_verified'] += members
            receipt['published_member_bytes_verified'] += size
            save_receipt(receipt_path, receipt)
        require(receipt['parts_verified'] == len(manifest['parts']) and
                receipt['members_verified'] == expected_members and
                receipt['published_member_bytes_verified'] == published_bytes, 'FINAL_COUNT_MISMATCH')
        receipt['status'], receipt['ended_at'] = 'VERIFIED', utcnow()
        save_receipt(receipt_path, receipt)
        return receipt
    except BaseException as error:
        code = str(error) if isinstance(error, VerificationError) else (
            'INTERRUPTED' if isinstance(error, (KeyboardInterrupt, SystemExit)) else
            'UNEXPECTED_VERIFICATION_ERROR')
        receipt.update(status='FAILED', failure_code=code, ended_at=utcnow())
        try:
            save_receipt(receipt_path, receipt)
        except Exception:
            pass
        raise VerificationError(code) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256')
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = run(args.manifest, args.receipt, args.manifest_sha256)
    except VerificationError as error:
        print('verification failed: ' + str(error), file=sys.stderr)
        return 1
    print(f'verified {receipt["cases_verified"]} cases, {receipt["parts_verified"]} parts, '
          f'{receipt["members_verified"]} members; anonymous=True', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
