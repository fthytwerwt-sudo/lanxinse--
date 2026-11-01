#!/usr/bin/env python3
"""Read-only upload preflight: heuristics, not a proof of disclosure safety."""
import argparse
import hashlib
import io
import json
import logging
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

WORKSPACE = Path('/Volumes/WD_BLACK/澜心社剪辑')
VOLUME = Path('/Volumes/WD_BLACK')
LFS_RECOMMEND_BYTES = 50 * 1024 * 1024
LFS_REQUIRED_BYTES = 100 * 1024 * 1024
TEXT_LIMIT = 10 * 1024 * 1024
ZIP_TOTAL_LIMIT = 32 * 1024 * 1024
ZIP_MEMBER_LIMIT = 8 * 1024 * 1024
ZIP_COUNT_LIMIT = 2048
PDF_PAGE_LIMIT = 200
SECRET = re.compile(r'\b(?:sk-[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?i:\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret)\b)[\"\']?\s*[:=]\s*[\"\']?([A-Za-z0-9_./+=-]{24,})')
PRIVATE_CLASS = re.compile(r'(?i)(?:保密级别|密级|classification|sensitivity)[\"\']?\s*[:：=]\s*[\"\']?(?:客户内部|内部机密|机密|秘密|私密|private|confidential|internal)')
PERSON_NAME = re.compile(r'''(?i)(?:客户姓名|真实姓名|client[_-]?name|customer[_-]?name)["']?\s*[:：=]\s*["']?([一-鿿]{2,6}|[a-z][a-z .'-]{1,40})''')
PERSON_PHONE = re.compile(r'''(?i)(?:手机号|手机号码|客户电话|联系电话|mobile[_-]?(?:number|phone)?|phone[_-]?number)["']?\s*[:：=]\s*["']?(?:\+?86[- ]?)?1[3-9]\d{9}\b''')
PERSON_ID = re.compile(r'''(?i)(?:身份证号|身份证号码|id[_-]?number|identity[_-]?number)["']?\s*[:：=]\s*["']?(?:\d{17}[\dX]|\d{15})(?![\dX])''')
NAME_PLACEHOLDERS = {'待确认','未填写','请填写','不提供','匿名','示例','无','none','null','unknown','not provided','placeholder','example'}
DRIVE = re.compile(r'https?://(?:drive\.google\.com/(?:file/d/|drive/(?:u/\d+/)?folders/|open\?id=)|docs\.google\.com/(?:document|spreadsheets|presentation|forms)/d/)', re.I)
TEXT_EXT = {'.md','.txt','.py','.js','.ts','.tsx','.jsx','.json','.jsonl','.csv','.tsv','.yaml','.yml','.toml','.xml','.html','.htm','.css','.sh','.rs','.go','.java','.c','.h','.cpp','.sql','.ini','.conf','.rst','.svg','.rels','.gitignore','.gitattributes'}
ARCHIVE_EXT = {'.docx','.xmind'}
SEVERITY = {'pass':0, 'review':1, 'block':2}


def workspace_check():
    if not WORKSPACE.is_dir() or WORKSPACE.resolve() != WORKSPACE:
        raise ValueError('workspace_unavailable')
    mounts = subprocess.run(['mount'], text=True, capture_output=True, check=True).stdout.splitlines()
    if not any(' on /Volumes/WD_BLACK (' in line for line in mounts): raise ValueError('workspace_not_mounted')
    if os.stat(WORKSPACE).st_dev != os.stat(VOLUME).st_dev: raise ValueError('workspace_volume_mismatch')


def git(repo, *args):
    return subprocess.run(['git','-C',str(repo),*(['--literal-pathspecs'] if args and args[0] == 'ls-files' else []),*args], capture_output=True, text=True)


def repo_path(repo):
    workspace_check()
    requested = Path(repo).absolute()
    resolved = requested.resolve(strict=True)
    if not resolved.is_relative_to(WORKSPACE) or resolved != requested: raise ValueError('repo_outside_or_symlink')
    found = git(resolved, 'rev-parse','--show-toplevel','--absolute-git-dir')
    if found.returncode != 0: raise ValueError('not_git_repository')
    lines = found.stdout.strip().splitlines()
    if len(lines) != 2 or Path(lines[0]).resolve() != resolved or not Path(lines[1]).resolve().is_relative_to(WORKSPACE):
        raise ValueError('wrong_repo_or_git_dir')
    return resolved


def resolve_candidate(repo, path):
    if not isinstance(path, str) or not path or '\x00' in path: raise ValueError('invalid_path')
    supplied = Path(path)
    lexical = supplied if supplied.is_absolute() else repo / supplied
    if '..' in lexical.parts or not lexical.is_relative_to(repo): raise ValueError('path_outside_repo')
    cur = repo
    for part in lexical.relative_to(repo).parts:
        cur = cur / part
        if cur.is_symlink(): raise ValueError('symlink_path')
    actual = lexical.resolve(strict=True)
    if not actual.is_relative_to(repo) or not actual.is_file(): raise ValueError('not_regular_file')
    return actual, actual.relative_to(repo).as_posix()


def sensitive_filename(name):
    n = name.lower()
    if n == '.env.example': return False
    return (n == '.env' or n.startswith('.env.') or n in {'id_rsa','id_ed25519','credentials.json','authorized_keys'}
            or n.endswith(('.pem','.key','.p12','.pfx','.secret')) or bool(re.search(r'(?:^|[_-])(?:api[_-]?key|token|password|secret)(?:[_.-]|$)',n)))


def private_filename(name):
    return bool(re.search(r'(?i)合同|客户名单|机密|私密|私有|contract|private', name))


def add(result, severity, reason):
    if SEVERITY[severity] > SEVERITY[result['status']]: result['status'] = severity
    if reason not in result['reasons']: result['reasons'].append(reason)


def scan_text(text, result):
    if SECRET.search(text): add(result,'block','secret_pattern')
    if PRIVATE_CLASS.search(text): add(result,'block','private_classification')
    if PERSON_PHONE.search(text) or PERSON_ID.search(text): add(result,'block','personal_information_field')
    if any(m.group(1).strip().lower() not in NAME_PLACEHOLDERS for m in PERSON_NAME.finditer(text)):
        add(result,'review','personal_name_field')
    if DRIVE.search(text):
        if any(DRIVE.search(line) and re.search(r'私有|私人|内部|(?i:private|confidential)', line) for line in text.splitlines()):
            add(result,'block','private_drive_link')
        else: add(result,'review','drive_link_visibility_unverified')


def decode(data, result):
    try:
        if data.startswith((b'\xff\xfe', b'\xfe\xff')): return data.decode('utf-16')
        return data.decode('utf-8-sig')
    except UnicodeError:
        add(result,'review','text_decode_incomplete')
        return None


def inspect_text(data, result, suffix=''):
    text = decode(data, result)
    if text is None: return
    if '\x00' in text: add(result,'review','text_contains_nul'); return
    scan_text(text, result)
    if suffix == '.json':
        try: scan_text(json.dumps(json.loads(text), ensure_ascii=False), result)
        except (ValueError, RecursionError): add(result,'review','invalid_json')
    if suffix in {'.xml', '.rels'}:
        try:
            root = ET.fromstring(text)
            scan_text(''.join(root.itertext()), result)
            for node in root.iter():
                if node.text: scan_text(node.text, result)
                if node.tail: scan_text(node.tail, result)
                for value in node.attrib.values(): scan_text(value, result)
        except (ET.ParseError, ValueError, RecursionError): add(result,'review','invalid_xml')


def inspect_archive(path, result):
    try:
        with zipfile.ZipFile(path) as z:
            entries = z.infolist()
            member_names = {e.filename for e in entries}
            if path.suffix.lower() == '.docx' and not {'[Content_Types].xml','word/document.xml'}.issubset(member_names):
                add(result,'review','archive_structure_incomplete')
            if path.suffix.lower() == '.xmind' and not ({'content.json','content.xml'} & member_names):
                add(result,'review','archive_structure_incomplete')
            if len(entries) > ZIP_COUNT_LIMIT or sum(e.file_size for e in entries) > ZIP_TOTAL_LIMIT:
                add(result,'review','archive_expansion_limit'); return
            seen = set()
            for entry in entries:
                name = entry.filename
                parts = PurePosixPath(name).parts
                kind = stat.S_IFMT(entry.external_attr >> 16)
                key = unicodedata.normalize('NFC', name).casefold().rstrip('/')
                if not name or name.startswith('/') or '\\' in name or '\x00' in name or '..' in parts or kind not in (0,stat.S_IFREG,stat.S_IFDIR) or key in seen:
                    add(result,'block','archive_unsafe_member'); return
                seen.add(key)
                if entry.is_dir(): continue
                if entry.file_size > ZIP_MEMBER_LIMIT: add(result,'review','archive_member_limit'); continue
                data = z.read(entry)
                suffix = Path(name).suffix.lower()
                if suffix in TEXT_EXT or suffix in {'.xml','.json','.rels'}:
                    inspect_text(data, result, suffix)
                else:
                    text = decode(data, {'status':'pass','reasons':[]})
                    if text is not None and '\x00' not in text: scan_text(text, result)
                    add(result,'review','archive_binary_content_uninspected')
    except Exception:
        add(result,'review','archive_unreadable')


def deref(obj):
    return obj.get_object() if hasattr(obj,'get_object') else obj


def inspect_pdf(path, result):
    try:
        from pypdf import PdfReader
    except ImportError:
        add(result,'review','pdf_dependency_missing'); return
    previous_logging_disable = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        with path.open('rb') as stream:
            reader = PdfReader(stream)
            if reader.is_encrypted: add(result,'review','pdf_encrypted'); return
            catalog = deref(reader.trailer.get('/Root', {}))
            names = deref(catalog.get('/Names', {}))
            if names.get('/EmbeddedFiles') or names.get('/JavaScript') or any(catalog.get(k) for k in ('/AF','/AcroForm','/Collection','/OpenAction','/AA','/Outlines','/Metadata')):
                add(result,'review','pdf_embedded_or_form_content')
            if len(reader.pages) > PDF_PAGE_LIMIT: add(result,'review','pdf_page_limit'); return
            if len(reader.pages) == 0: add(result,'review','pdf_no_pages')
            meta = reader.metadata
            if meta:
                for value in meta.values():
                    if isinstance(value,str): scan_text(value,result)
            for page in reader.pages:
                if page.get('/AA') or page.get('/AF'): add(result,'review','pdf_embedded_or_form_content')
                text = page.extract_text() or ''
                if not text.strip(): add(result,'review','pdf_page_no_extractable_text')
                scan_text(text,result)
                for annot_ref in deref(page.get('/Annots', [])):
                    annot = deref(annot_ref)
                    if annot.get('/Subtype') in ('/FileAttachment','/RichMedia','/Screen','/3D') or annot.get('/FS'):
                        add(result,'review','pdf_embedded_or_form_content')
                    for key in ('/Contents','/T','/Subj'):
                        val = deref(annot.get(key))
                        if isinstance(val,str): scan_text(val,result)
                    action = deref(annot.get('/A', {}))
                    if action:
                        if action.get('/S') not in (None, '/URI', '/GoTo'):
                            add(result,'review','pdf_action_uninspected')
                        uri = deref(action.get('/URI'))
                        if isinstance(uri, str): scan_text(uri,result)
                resources = deref(page.get('/Resources', {}))
                xobjects = deref(resources.get('/XObject', {}))
                if any(deref(obj).get('/Subtype') in ('/Image','/Form') for obj in xobjects.values()):
                    add(result,'review','pdf_visual_content_uninspected')
    except Exception:
        add(result,'review','pdf_unreadable_or_incomplete')
    finally:
        logging.disable(previous_logging_disable)


def inspect_file(repo, path):
    result = {'path':path, 'status':'pass', 'route':'unknown', 'sha256':None, 'size_bytes':None, 'git_state':'unknown', 'reasons':[]}
    try:
        repo = repo_path(repo)
        actual, rel = resolve_candidate(repo, path)
        result['path'] = rel
        if sensitive_filename(actual.name) or SECRET.search(rel):
            result['path'] = '[sensitive-name]'
            add(result,'block','credential_filename')
            return result
        if private_filename(actual.name): add(result,'review','sensitive_filename')
        tracked = git(repo,'ls-files','--error-unmatch','--',rel)
        ignored = git(repo,'check-ignore','--no-index','-q','--',rel)
        if ignored.returncode not in (0,1) or tracked.returncode not in (0,1): raise ValueError('git_check_failed')
        result['git_state'] = 'tracked_ignored' if tracked.returncode == 0 and ignored.returncode == 0 else ('tracked' if tracked.returncode == 0 else ('ignored_untracked' if ignored.returncode == 0 else 'untracked'))
        if result['git_state'] == 'ignored_untracked': add(result,'review','git_ignored_untracked')
        result['size_bytes'] = actual.stat().st_size
        h = hashlib.sha256()
        with actual.open('rb') as source:
            for block in iter(lambda: source.read(1024 * 1024), b''): h.update(block)
        result['sha256'] = h.hexdigest()
        if result['size_bytes'] > LFS_REQUIRED_BYTES:
            attrs = git(repo, 'check-attr', 'filter', '--', rel)
            has_lfs_filter = attrs.returncode == 0 and attrs.stdout.rstrip().endswith(': lfs')
            if has_lfs_filter and shutil.which('git-lfs'): add(result,'review','large_file_lfs_verify')
            else: add(result,'block','lfs_required')
        elif result['size_bytes'] > LFS_RECOMMEND_BYTES: add(result,'review','lfs_recommended')
        suffix = actual.suffix.lower()
        if suffix in ARCHIVE_EXT:
            result['route']='binary'; inspect_archive(actual,result)
        elif suffix == '.pdf':
            result['route']='binary'; inspect_pdf(actual,result)
        elif suffix in TEXT_EXT or actual.name in {'.gitignore','.gitattributes'}:
            result['route']='text'
            if result['size_bytes'] > TEXT_LIMIT: add(result,'review','text_scan_limit')
            else: inspect_text(actual.read_bytes(),result,suffix)
        else:
            result['route']='binary'; add(result,'review','unknown_file_format')
    except (OSError,ValueError,subprocess.SubprocessError):
        result['path'] = '[invalid-or-outside-path]'
        add(result,'block','invalid_repo_or_candidate')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',required=True,help='workspace-internal Git repository root')
    parser.add_argument('paths',nargs='+',help='explicit paths within the repository')
    args = parser.parse_args()
    results = [inspect_file(args.repo,p) for p in args.paths]
    print(json.dumps({'disclaimer':'heuristic; not a proof of safety', 'results':results}, ensure_ascii=False, indent=2))
    return 2 if any(r['status']=='block' for r in results) else (1 if any(r['status']=='review' for r in results) else 0)

if __name__ == '__main__': sys.exit(main())
