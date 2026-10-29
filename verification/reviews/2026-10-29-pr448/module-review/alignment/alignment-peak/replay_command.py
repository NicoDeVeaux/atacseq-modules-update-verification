"""Explicitly replay one saved local Docker command into a fresh output folder."""
from pathlib import Path
import argparse
import json
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command_json', type=Path)
    parser.add_argument('new_output_directory', type=Path)
    args = parser.parse_args()
    saved = json.loads(args.command_json.read_text())
    command = list(saved['command'])
    if command[:5] != ['docker', '--context', 'colima', 'run', '--rm']:
        raise ValueError('Expected an archived Colima Docker run command')
    destination = args.new_output_directory.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    writable = []
    for i, value in enumerate(command):
        if i and command[i - 1] == '-v' and not value.endswith(':ro'):
            source, container_path = value.rsplit(':', 1)
            writable.append((i, container_path))
    if len(writable) != 1 or writable[0][1] not in {'/out', '/output'}:
        raise ValueError('Expected exactly one archived output mount')
    index, container_path = writable[0]
    command[index] = f'{destination}:{container_path}'
    command.insert(5, '--pull=never')
    is_stdout_sam = 'bwa' in command and 'mem' in command or 'bowtie2' in command
    with (destination / ('alignments.sam' if is_stdout_sam else 'stdout.txt')).open('w') as out:
        result = subprocess.run(command, text=True, stdout=out, stderr=subprocess.PIPE)
    (destination / 'stderr.txt').write_text(result.stderr)
    (destination / 'replay-record.json').write_text(json.dumps({'source_command': str(args.command_json.resolve()), 'command': command, 'exit_code': result.returncode}, indent=2) + '\n')
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
