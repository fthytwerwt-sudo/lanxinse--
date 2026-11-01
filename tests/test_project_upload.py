"""Upload preflight tests. All generated Git repositories stay inside WD_BLACK."""
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from pypdf import PdfWriter
from reportlab.pdfgen import canvas

ROOT = Path('/Volumes/WD_BLACK/澜心社剪辑')
SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check_project_upload.py'
spec = importlib.util.spec_from_file_location('upload_check', SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class UploadTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.local_runtime/tests').mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / '.local_runtime/tests')
        self.repo = Path(self.tmp.name)
        env = os.environ.copy()
        env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
        self.env = env
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True, env=env)
    def tearDown(self): self.tmp.cleanup()
    def write(self, name, data):
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode())
        return p
    def run_check(self, name): return check.inspect_file(self.repo, name)
    def test_text_route_and_ordinary_security_discussion(self):
        self.write('rules.md', '禁止提交密钥，客户合同应保存在私有存储。')
        result = self.run_check('rules.md')
        self.assertEqual((result['status'], result['route']), ('pass', 'text'))
        self.assertEqual(len(result['sha256']), 64)
    def test_ignored_untracked_and_ignored_tracked_distinguished(self):
        self.write('.gitignore', '*.pdf\n')
        self.write('one.pdf', b'not pdf')
        before = self.run_check('one.pdf')
        self.assertEqual(before['git_state'], 'ignored_untracked')
        subprocess.run(['git','-C',str(self.repo),'add','-f','--','one.pdf'], check=True, env=self.env)
        after = self.run_check('one.pdf')
        self.assertEqual(after['git_state'], 'tracked_ignored')
    def test_credentials_and_values_are_redacted(self):
        value = 'sk-' + 'AbCdEf0123456789' * 3
        self.write('config.txt', 'api_key=' + value)
        result = self.run_check('config.txt')
        self.assertEqual(result['status'], 'block')
        self.assertNotIn(value, str(result))
        self.write('.env', 'sample')
        self.assertEqual(self.run_check('.env')['status'], 'block')
        gh_value = 'ghp_' + 'A1' * 20
        self.write('source.py', 'token = "' + gh_value + '"')
        result = self.run_check('source.py')
        self.assertEqual(result['status'], 'block')
        self.assertNotIn(gh_value, str(result))
    def test_private_classification_and_drive_link(self):
        self.write('internal.md', '保密级别：' + '客户内部\n')
        self.assertEqual(self.run_check('internal.md')['status'], 'block')
        self.write('classified.json', '{"classification":"' + 'private"}')
        self.assertEqual(self.run_check('classified.json')['status'], 'block')
        self.write('drive.md', 'https://' + 'drive.google.com/drive/folders/abcdef123456\n')
        self.assertEqual(self.run_check('drive.md')['status'], 'review')
        self.write('private_link.md', '私有 Drive: ' + 'https://' + 'drive.google.com/drive/folders/abcdef123456')
        self.assertEqual(self.run_check('private_link.md')['status'], 'block')
    def test_sensitive_filenames_and_assigned_personal_data(self):
        self.write('客户合同.docx', b'not a zip')
        self.assertIn(self.run_check('客户合同.docx')['status'], ('block','review'))
        self.write('private_notes.md', 'safe contents')
        self.assertIn(self.run_check('private_notes.md')['status'], ('block','review'))
        values = [('customer.md', '客户姓名：' + '张三'), ('phone.md', '手机号：' + '13800138000'),
                  ('id.md', '身份证号：' + '11010519491231002X'), ('contact.json', '{"client_name":"' + 'Wang Fan"}')]
        for name, content in values:
            self.write(name, content)
            result = self.run_check(name)
            self.assertIn(result['status'], ('block','review'))
            self.assertNotIn(content, str(result))
        self.write('policy.md', '不得公开合同、个人隐私和客户姓名、手机号与身份证号；请在内部按需保护。')
        self.assertEqual(self.run_check('policy.md')['status'], 'pass')
        self.write('placeholder.md', '客户姓名：待确认')
        self.assertEqual(self.run_check('placeholder.md')['status'], 'pass')

    def test_realpath_and_symlink_escape_rejected(self):
        self.write('ok.md', 'ok')
        (self.repo / 'outside').symlink_to('/', target_is_directory=True)
        self.assertEqual(self.run_check('outside/Library/x.md')['status'], 'block')
        self.assertEqual(self.run_check('../outside.md')['status'], 'block')
    def test_size_lfs_thresholds(self):
        self.write('medium.txt', b'x' * 51)
        self.write('large.txt', b'x' * 101)
        with patch.object(check, 'LFS_RECOMMEND_BYTES', 50), patch.object(check, 'LFS_REQUIRED_BYTES', 100):
            self.assertIn('lfs_recommended', self.run_check('medium.txt')['reasons'])
            self.assertIn('lfs_required', self.run_check('large.txt')['reasons'])
    def test_large_file_with_lfs_filter_still_needs_verification(self):
        self.write('large.txt', b'x' * 101)
        self.write('.gitattributes', '*.txt filter=lfs diff=lfs merge=lfs -text\n')
        with patch.object(check, 'LFS_REQUIRED_BYTES', 100), patch.object(check.shutil, 'which', return_value='/fake/git-lfs'):
            result = self.run_check('large.txt')
        self.assertEqual(result['status'], 'review')
        self.assertIn('large_file_lfs_verify', result['reasons'])

    def test_docx_and_xmind_inspect_comments_and_json(self):
        value = 'sk-' + 'AbCdEf0123456789' * 3
        for name, member in [('doc.docx','word/comments.xml'), ('mind.xmind','content.json')]:
            with zipfile.ZipFile(self.repo / name, 'w') as z:
                z.writestr(member, 'api_key=' + value)
            result = self.run_check(name)
            self.assertEqual((result['status'],result['route']),('block','binary'))
            self.assertNotIn(value, str(result))
    def test_embedded_metadata_and_escaped_json_values(self):
        value = 'A1b2C3d4' * 5
        with zipfile.ZipFile(self.repo / 'mind.xmind', 'w') as z:
            z.writestr('content.json', '{"api_key":"' + value + '"}')
            z.writestr('metadata.xml', '<root><item>safe</item></root>')
        result = self.run_check('mind.xmind')
        self.assertEqual(result['status'], 'block')
        self.assertNotIn(value, str(result))

    def test_empty_package_and_binary_members_need_review(self):
        with zipfile.ZipFile(self.repo / 'empty.docx', 'w'): pass
        self.assertEqual(self.run_check('empty.docx')['status'], 'review')
        with zipfile.ZipFile(self.repo / 'image.docx', 'w') as z:
            z.writestr('[Content_Types].xml', '<Types/>')
            z.writestr('word/document.xml', '<doc/>')
            z.writestr('word/media/image.png', 'not inspected pixels')
        result = self.run_check('image.docx')
        self.assertEqual(result['status'], 'review')
        self.assertIn('archive_binary_content_uninspected', result['reasons'])

    def test_zip_traversal_and_expansion_limit(self):
        with zipfile.ZipFile(self.repo / 'evil.xmind', 'w') as z: z.writestr('../escape.xml','hi')
        self.assertEqual(self.run_check('evil.xmind')['status'],'block')
        with zipfile.ZipFile(self.repo / 'large.docx', 'w') as z: z.writestr('word/document.xml','x'*100)
        with patch.object(check, 'ZIP_TOTAL_LIMIT', 50):
            self.assertEqual(self.run_check('large.docx')['status'], 'review')
    def test_pdf_text_pass_and_blank_encrypted_review(self):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer); c.drawString(72, 750, 'Public example content.'); c.save()
        self.write('plain.pdf', buffer.getvalue())
        self.assertEqual(self.run_check('plain.pdf')['status'], 'pass')
        writer = PdfWriter(); writer.add_blank_page(300,300)
        writer.write(self.repo / 'blank.pdf')
        self.assertEqual(self.run_check('blank.pdf')['status'], 'review')
        writer.encrypt('password'); writer.write(self.repo / 'encrypted.pdf')
        self.assertEqual(self.run_check('encrypted.pdf')['status'], 'review')
    def test_pdf_clickable_drive_link_needs_review(self):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer); c.drawString(72, 750, 'Open document')
        c.linkURL('https://' + 'drive.google.com/drive/folders/exampleid', (72,740,150,760))
        c.save(); self.write('link.pdf', buffer.getvalue())
        self.assertIn('drive_link_visibility_unverified', self.run_check('link.pdf')['reasons'])

    def test_pdf_without_pypdf_is_review(self):
        import sys
        self.write('normal.pdf', b'%PDF')
        with patch.dict(sys.modules, {'pypdf': None}):
            result = self.run_check('normal.pdf')
        self.assertIn('pdf_dependency_missing', result['reasons'])
        self.assertEqual(result['status'], 'review')

    def test_pdf_attachment_requires_review(self):
        writer = PdfWriter(); writer.add_blank_page(300,300)
        writer.add_attachment('sample.txt', b'some embedded text')
        writer.write(self.repo / 'attached.pdf')
        result = self.run_check('attached.pdf')
        self.assertEqual(result['status'], 'review')
        self.assertIn('pdf_embedded_or_form_content', result['reasons'])

    def test_corrupt_pdf_does_not_log_file_content(self):
        value = b'not-pdf-private-marker'
        self.write('broken.pdf', value)
        import sys
        result = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(self.repo), 'broken.pdf'], capture_output=True, text=True)
        self.assertNotIn('not-p', result.stdout + result.stderr)

    def test_corrupt_or_unrecognized_file_is_review(self):
        self.write('broken.pdf', b'not a pdf')
        self.assertEqual(self.run_check('broken.pdf')['status'], 'review')
        self.write('unknown.dat', b'\x00\xff')
        self.assertEqual(self.run_check('unknown.dat')['status'], 'review')

if __name__ == '__main__': unittest.main()
