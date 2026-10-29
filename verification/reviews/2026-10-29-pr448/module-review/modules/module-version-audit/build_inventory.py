"""Inventory declared pins from PR448's actual first parent and merge tree."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import csv
import hashlib
import json
import posixpath
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / 'atacseq-pr448-review/source'
OLD = '4177ea95c56e15fdbdc52f6e210c3329ff69167b'
NEW = 'a51bee0178045b29cd9f034e58f4de6b80bc91db'
REPOSITORY = 'https://github.com/nf-core/atacseq'


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args])


@lru_cache(None)
def blob(ref, path):
    result = subprocess.run(['git', '-C', str(SOURCE), 'show', ref + ':' + path], capture_output=True)
    return result.stdout.decode() if result.returncode == 0 else None


def source_url(ref, path):
    return f'{REPOSITORY}/blob/{ref}/{path}'


def directive(text, name):
    match = re.search(r'^[ \t]*' + name + r'''[ \t]+(['"])(.*?)\1''', text, re.M | re.S)
    return {'expression': match.group(0).strip(), 'value': match.group(2), 'line': text.count('\n', 0, match.start()) + 1} if match else None


def dependency(specifier, line=None):
    value = specifier.strip().strip('\'"')
    match = re.fullmatch(r'(?:(?P<channel>[\w.-]+)::)?(?P<name>[\w.+-]+)(?P<spec>[=<>!~].*)?', value)
    return {'raw': value, 'name': match.group('name') if match else None, 'channel': match.group('channel') if match else None, 'version_specifier': match.group('spec') if match else None, 'line': line}


def conda_pins(ref, directory, main):
    selected = directive(main, 'conda')
    environment_path = directory + '/environment.yml'
    environment = blob(ref, environment_path)
    dependencies = []
    if selected and 'environment.yml' in selected['value'] and environment is not None:
        active = False
        for number, line in enumerate(environment.splitlines(), 1):
            if line.startswith('dependencies:'):
                active = True
            elif active:
                match = re.match(r'\s+-\s+([^#]+)', line)
                if match:
                    dependencies.append(dependency(match.group(1).strip(), number))
    elif selected:
        dependencies = [dependency(value) for value in shlex.split(selected['value'])]
    return {'directive': selected, 'environment_path': environment_path if environment is not None else None, 'environment_source_url': source_url(ref, environment_path) if environment is not None else None, 'dependencies': dependencies, 'environment_text': environment}


def image(reference):
    result = {'reference': reference, 'image_name': None, 'tag': None, 'version_label': None, 'digest': None}
    digest = re.search(r'(?:sha256[:/](?:[0-9a-f]{2}/)?)([0-9a-f]{64})', reference)
    if digest:
        result['digest'] = digest.group(1)
    last = reference.rsplit('/', 1)[-1]
    if ':' in last and not reference.endswith('/data'):
        name, tag = last.split(':', 1)
        result.update(image_name=name, tag=tag)
        prefix = tag.split('--', 1)[0]
        if re.fullmatch(r'v?\d+(?:\.\d+)*(?:[a-z]\d+)?', prefix) and ('.' in prefix or len(prefix.lstrip('v')) <= 6):
            result['version_label'] = prefix.lstrip('v')
    return result


def containers(main):
    selected = directive(main, 'container')
    references = []
    if selected:
        if '${' not in selected['value']:
            candidates = [selected['value']]
        else:
            candidates = re.findall(r"'([^']+)'", selected['value'])
        references = [image(value) for value in candidates if '/' in value and (':' in value or value.startswith('https://'))]
    return {'directive': selected, 'references': references}


def normalized(value):
    return re.sub('[^a-z0-9]', '', value.lower())


def metadata(ref, directory, tool_hints):
    path = directory + '/meta.yml'
    text = blob(ref, path)
    tools, urls = [], []
    if text:
        block = re.search(r'^tools:\s*\n(.*?)(?=^\S|\Z)', text, re.M | re.S)
        if block:
            tools = re.findall(r'^\s{2}-\s+([^:\n]+):', block.group(1), re.M)
            for match in re.finditer(r'^\s+(homepage|documentation|source|source_url|repository):\s*[\'\"]?(https?://[^\s\'\"]+)', block.group(1), re.M):
                urls.append({'kind': match.group(1), 'url': match.group(2), 'metadata_path': path, 'source_url': source_url(ref, path)})
    citations = []
    names = {normalized(value) for value in tools + tool_hints if value}
    aliases = {'subread': 'featurecounts', 'trimgalore': 'trimgalore', 'picard': 'picardtools', 'ucsc': 'ucsctools'}
    names.update(aliases[value] for value in list(names) if value in aliases)
    for match in re.finditer(r'^- \[([^\]]+)\]\((https?://[^)]+)\)', blob(ref, 'CITATIONS.md') or '', re.M):
        if normalized(match.group(1)) in names:
            citations.append({'label': match.group(1), 'url': match.group(2), 'source_url': source_url(ref, 'CITATIONS.md')})
    return {'meta_path': path if text else None, 'tool_names': tools, 'tool_urls': urls, 'citations': citations}


def locked(ref):
    data = json.loads(blob(ref, 'modules.json'))
    result = {}
    for repository, groups in data.get('repos', {}).items():
        for group, namespaces in groups.items():
            if group not in ('modules', 'subworkflows'):
                continue
            for namespace, entries in namespaces.items():
                for name, item in entries.items():
                    result[group + '/' + namespace + '/' + name] = {'repository': repository, **item}
    return data, result


def reachable(ref):
    files = set(git('ls-tree', '-r', '--name-only', ref).decode().splitlines())
    result, pending = set(), ['main.nf']
    while pending:
        path = pending.pop()
        if path in result:
            continue
        result.add(path)
        text = blob(ref, path) or ''
        for match in re.finditer(r'include\s*\{.*?\}\s*from\s*[\'\"]([^\'\"]+)[\'\"]', text, re.S):
            target = posixpath.normpath(posixpath.join(posixpath.dirname(path), match.group(1)))
            for candidate in (target, target + '.nf', target + '/main.nf'):
                if candidate in files and candidate.endswith('.nf'):
                    pending.append(candidate)
                    break
    return result


def snapshot(ref, directory, main_path, lock, reach):
    text = blob(ref, main_path)
    if text is None:
        return None
    pins = conda_pins(ref, directory, text)
    hints = [directory.split('/')[-2] if '/' in directory else directory, directory.split('/')[-1], posixpath.basename(main_path).removesuffix('.nf')]
    hints += [item['name'] for item in pins['dependencies'] if item['name']]
    reported_tools = re.findall(r'''tuple\s+val\([^\n]*?task\.process[^\n]*?\),\s*val\(['"]([^'"]+)['"]\)''', text)
    hints += reported_tools + [name.removeprefix('bioconductor-').removeprefix('r-') for name in hints]
    return {'main_path': main_path, 'source_url': source_url(ref, main_path), 'main_sha256': hashlib.sha256(text.encode()).hexdigest(), 'module_lock': lock, 'upstream_module_sha': lock.get('git_sha') if lock else None, 'reported_tools': reported_tools, 'conda': pins, 'container': containers(text), 'metadata': metadata(ref, directory, hints), 'reachable_from_pipeline_main': main_path in reach}


def versions(side):
    if not side:
        return {}, set()
    conda = {item['name']: item['version_specifier'] for item in side['conda']['dependencies'] if item['name']}
    labels = {item['version_label'] for item in side['container']['references'] if item['version_label']}
    return conda, labels


def main():
    assert git('show', '-s', '--format=%P', NEW).decode().split()[0] == OLD
    old_schema, old_lock = locked(OLD)
    new_schema, new_lock = locked(NEW)
    changes = [line.split('\t', 1) for line in git('diff', '--no-renames', '--name-status', OLD, NEW, '--', 'modules', 'subworkflows').decode().splitlines()]
    changed_paths = [path for status, path in changes]
    entries = set(old_lock) | set(new_lock)
    for path in changed_paths:
        if path.startswith(('modules/nf-core/', 'subworkflows/nf-core/')):
            if path.endswith('/main.nf') and '/tests/' not in path:
                entries.add(path[:-8])
        elif path.startswith(('modules/local/', 'subworkflows/local/')) and path.endswith('.nf'):
            entries.add(path)
    reach = {OLD: reachable(OLD), NEW: reachable(NEW)}
    records = []
    for entry in sorted(entries):
        local = '/local/' in entry
        related = [path for path in changed_paths if path == entry or path.startswith(entry + '/')]
        old_revision = old_lock.get(entry, {}).get('git_sha')
        new_revision = new_lock.get(entry, {}).get('git_sha')
        if not related and old_revision == new_revision:
            continue
        directory = posixpath.dirname(entry) if local else entry
        path = entry if local else entry + '/main.nf'
        old = snapshot(OLD, directory, path, old_lock.get(entry), reach[OLD])
        new = snapshot(NEW, directory, path, new_lock.get(entry), reach[NEW])
        old_conda, old_tags = versions(old)
        new_conda, new_tags = versions(new)
        conda_changed = sorted(key for key in old_conda.keys() & new_conda.keys() if old_conda[key] != new_conda[key])
        tags_changed = bool(old_tags and new_tags and old_tags != new_tags)
        pin_changed = bool(conda_changed or tags_changed)
        state = 'added' if old is None else 'removed' if new is None else 'updated'
        runtime = any(side and (side['conda']['directive'] or side['container']['directive']) for side in (old, new))
        ambiguous = bool(runtime and not old_tags and not new_tags and not any(old_conda.values()) and not any(new_conda.values()))
        classification = state + '_component' if state != 'updated' else 'subworkflow_wiring_only' if not runtime else 'declared_version_changed' if pin_changed else 'opaque_or_unpinned_versions' if ambiguous else 'same_declared_versions_build_or_wiring_changed'
        records.append({'kind': ('local_' if local else 'nfcore_') + ('module' if entry.startswith('modules/') else 'subworkflow'), 'name': entry.split('/', 2)[2].removesuffix('.nf'), 'path': entry, 'status': state, 'changed_files': related, 'old': old, 'new': new, 'module_lock_revision_changed': old_revision != new_revision, 'main_source_changed': not old or not new or old['main_sha256'] != new['main_sha256'], 'tool_version_classification': classification, 'declared_tool_version_changed': pin_changed if state == 'updated' and runtime and not ambiguous else None, 'changed_conda_package_specifiers': conda_changed, 'added_conda_packages': sorted(new_conda.keys() - old_conda.keys()), 'removed_conda_packages': sorted(old_conda.keys() - new_conda.keys()), 'container_version_labels_changed': tags_changed, 'notes': []})
    covered = {path for record in records for path in record['changed_files']}
    assert set(changed_paths) <= covered, sorted(set(changed_paths) - covered)
    by_name = {record['path']: record for record in records}
    assert versions(by_name['modules/nf-core/trimgalore']['old'])[1] == {'0.6.10'}
    assert versions(by_name['modules/nf-core/trimgalore']['new'])[1] == {'2.1.0'}
    assert versions(by_name['modules/nf-core/subread/featurecounts']['old'])[1] == {'2.0.1'}
    assert versions(by_name['modules/nf-core/subread/featurecounts']['new'])[1] == {'2.0.1'}
    assert by_name['modules/nf-core/multiqc']['new']['reachable_from_pipeline_main'] is False
    assert by_name['modules/local/multiqc.nf']['new']['reachable_from_pipeline_main'] is True
    for record in records:
        if record['new'] and not record['new']['reachable_from_pipeline_main']:
            record['notes'].append('No static include path from pipeline main; installed/updated does not mean executed.')
        for side_name in ('old', 'new'):
            side = record[side_name]
            if side and any(item['tag'] and item['version_label'] is None for item in side['container']['references']):
                record['notes'].append(side_name + ': opaque image tag; contents/package versions not inferred.')
    inventory = {'schema': 'nf-verify/pr448-declared-version-inventory/v1', 'repository': REPOSITORY, 'base': OLD, 'merge': NEW, 'merge_first_parent_verified': True, 'interpretation': 'Source-declared Conda specifiers and literal image references/tags only. No image was executed or inspected; a container label is not a resolved package manifest. Opaque image contents and unpinned dependencies remain unknown. Static include reachability covers possible branches, not a measured execution.', 'modules_json_schemas': {'old_top_keys': list(old_schema), 'new_top_keys': list(new_schema), 'old_sha256': hashlib.sha256(blob(OLD, 'modules.json').encode()).hexdigest(), 'new_sha256': hashlib.sha256(blob(NEW, 'modules.json').encode()).hexdigest()}, 'counts': {'records': len(records), 'by_kind': dict(Counter(record['kind'] for record in records)), 'by_version_classification': dict(Counter(record['tool_version_classification'] for record in records)), 'changed_files_covered': len(covered)}, 'records': records}
    ROOT.mkdir(exist_ok=True)
    (ROOT / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    columns = ['kind','name','status','old_module_sha','new_module_sha','classification','old_conda','new_conda','old_container_refs','new_container_refs','upstream_urls','new_reachable','notes']
    with (ROOT / 'inventory.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, columns, delimiter='\t')
        writer.writeheader()
        for record in records:
            row = {key: record[key] for key in ('kind','name','status')}
            row.update(classification=record['tool_version_classification'], notes='; '.join(record['notes']))
            urls = set()
            for label in ('old','new'):
                side = record[label]
                row[label + '_module_sha'] = side['upstream_module_sha'] if side else ''
                row[label + '_conda'] = '; '.join(item['raw'] for item in side['conda']['dependencies']) if side else ''
                row[label + '_container_refs'] = '; '.join(item['reference'] for item in side['container']['references']) if side else ''
                if side:
                    urls.update(item['url'] for item in side['metadata']['tool_urls'] + side['metadata']['citations'])
            row.update(upstream_urls='; '.join(sorted(urls)), new_reachable=record['new']['reachable_from_pipeline_main'] if record['new'] else '')
            writer.writerow(row)
    print(json.dumps(inventory['counts'], indent=2))


if __name__ == '__main__':
    main()
