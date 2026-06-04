import codecs

def read_file_auto(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw.startswith(b'\xff\xfe'):
        enc = 'utf-16-le'
    elif raw.startswith(b'\xfe\xff'):
        enc = 'utf-16-be'
    elif raw.startswith(b'\xef\xbb\xbf'):
        enc = 'utf-8-sig'
    else:
        enc = 'utf-8'
    with open(path, 'r', encoding=enc) as f:
        return f.readlines()

dev_lines_raw = read_file_auto(r'D:\ai_practice\prodict\app\dev.txt')
installed_lines_raw = read_file_auto(r'd:\EAM-AI\py311_installed.txt')

dev_lines = [line.strip().split('==')[0].lower() for line in dev_lines_raw if line.strip() and not line.startswith('#')]
installed_lines = [line.strip().split('==')[0].lower() for line in installed_lines_raw if line.strip()]

dev_set = set(dev_lines)
installed_set = set(installed_lines)

missing = dev_set - installed_set

skip = {
    'conda', 'conda-anaconda-telemetry', 'conda-anaconda-tos', 'conda-content-trust',
    'conda-libmamba-solver', 'conda-package-handling', 'conda_package_streaming',
    'anaconda-anon-usage', 'anaconda-auth', 'anaconda-cli-base', 'libmambapy',
    'menuinst', 'pycosat', 'boltons', 'frozendict', 'ruamel.yaml', 'ruamel.yaml.clib',
    'semver', 'truststore', 'win_inet_pton', 'win32_setctime', 'readchar', 'pkce',
    'keyring', 'jaraco.classes', 'jaraco.context', 'jaraco.functools', 'more-itertools',
    'pluggy', 'setuptools', 'wheel', 'pip', 'brotlicffi', 'ecdsa', 'archspec',
    'flasgger', 'flask', 'flask-sock', 'drf-spectacular', 'drf-spectacular-sidecar',
    'drf-yasg', 'django', 'django-cors-headers', 'djangorestframework', 'gunicorn',
    'mongoengine', 'motor', 'pymongo', 'pgvector', 'psycopg2-binary', 'db-dtypes',
    'google-api-core', 'google-auth', 'google-cloud-aiplatform', 'google-cloud-bigquery',
    'google-cloud-core', 'google-cloud-resource-manager', 'google-cloud-storage',
    'google-crc32c', 'google-resumable-media', 'googleapis-common-protos',
    'grpc-google-iam-v1', 'grpcio', 'grpcio-status', 'kubernetes', 'mistralai',
    'anthropic', 'vertexai', 'snowflake-connector-python', 'mcp', 'choreographer',
    'kaleido', 'eval_type_backport', 'logistro', 'durationpy', 'mmh3',
    'opentelemetry-api', 'opentelemetry-exporter-otlp-proto-common',
    'opentelemetry-exporter-otlp-proto-grpc', 'opentelemetry-proto',
    'opentelemetry-sdk', 'opentelemetry-semantic-conventions', 'pyproject_hooks',
    'build', 'shellingham', 'importlib_metadata', 'importlib_resources',
    'exceptiongroup', 'tomli', 'colorlog', 'coloredlogs', 'humanfriendly', 'config',
    'olefile', 'python-iso639', 'python-oxmsg', 'langdetect', 'rank-bm25', 'rapidfuzz',
    'emoji', 'docx2txt', 'filetype', 'unstructured', 'unstructured-client', 'pypdf',
    'simple-websocket', 'wsproto', 'simplejson', 'tabulate', 'ujson', 'pybase64',
    'pyreadline3', 'pywin32', 'comtypes', 'psutil', 'werkzeug', 'mistune', 'html5lib',
    'webencodings', 'markdown-it-py', 'pygments', 'mdurl', 'rich', 'inflection',
    'uritemplate', 'sqlparse', 'markdown', 'plotly', 'narwhals', 'altair', 'pydeck',
    'streamlit', 'watchdog', 'modelscope', 'numexpr', 'torchaudio', 'toml',
    'typing_extensions', 'typing-inspection', 'tzdata', 'urllib3', 'pydantic',
    'pydantic_core', 'pydantic-settings', 'pycryptodome', 'pysocks', 'python-dateutil',
    'python-docx', 'python-dotenv', 'python-jose', 'python-multipart', 'pywin32-ctypes',
    'referencing', 'requests', 'rpds-py', 'rsa', 'sniffio', 'starlette', 'tenacity',
    'tqdm', 'typer', 'typer-slim', 'uvicorn', 'websockets', 'zstandard', 'passlib',
    'pyjwt', 'pymysql', 'pillow', 'pandas', 'openai', 'numpy', 'msgpack', 'minio',
    'lxml', 'loguru', 'jinja2', 'jiter', 'jsonpatch', 'jsonpointer', 'jsonschema',
    'jsonschema-specifications', 'httpx', 'httpcore', 'httptools', 'h11', 'greenlet',
    'gitdb', 'gitpython', 'filelock', 'fastapi', 'distro', 'cryptography', 'click',
    'charset-normalizer', 'cffi', 'certifi', 'cachetools', 'blinker', 'bcrypt',
    'attrs', 'argon2-cffi', 'argon2-cffi-bindings', 'anyio', 'annotated-types',
    'annotated-doc', 'aiofiles',
}

missing_filtered = sorted([m for m in missing if m not in skip])

print('=== 参考项目需要但 py311 环境缺少的包 ===')
for m in missing_filtered:
    print(f'  {m}')
print(f'\n共缺少 {len(missing_filtered)} 个包')
