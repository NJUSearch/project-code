import os
import re
import csv
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from py2neo import Graph, Node, Relationship, NodeMatcher

tag_list = ['.a', '.app', '.class-file', '.hgtags', '.lib', '.net', '.net-1.1', '.net-2.0', '.net-3.5', '.net-4.0',
            '.net-assembly', '.net-reflector', '.obj', '16-bit', '24bit', '2d', '2d-games', '2d-vector', '3-tier',
            '32-bit', '32bit-64bit', '3d', '3d-engine', '3d-model', '3d-reconstruction', '3d-rendering', '3des',
            '3dsmax', '64bit', '68hc12', '7zip', '8051', 'a-star', 'aabb', 'aac', 'abbreviation', 'abc', 'abi', 'abort',
            'absolute', 'absolute-path', 'absolute-value', 'abstract-base-class', 'abstract-class',
            'abstract-data-type', 'abstract-factory', 'abstract-syntax-tree', 'abstraction', 'acc',
            'accelerate-framework', 'accelerator', 'access-control', 'access-denied', 'access-modifiers',
            'access-rights', 'access-specifier', 'access-violation', 'accessibility', 'accessor', 'accumulate',
            'accumulator', 'ace', 'ace-tao', 'acl', 'acoustics', 'acpi', 'action', 'actionscript', 'actionscript-3',
            'activation', 'activation-record', 'active-directory', 'active-objects', 'active-window', 'activemq',
            'activemq-cpp', 'activeqt', 'activesync', 'activex', 'activexobject', 'ada', 'adapter', 'adaptor', 'add-in',
            'add-on', 'addition', 'addr2line', 'addressof', 'adjacency-list', 'adjacency-matrix', 'adjustment',
            'adler32', 'administrator', 'ado', 'ado.net', 'adobe', 'adobe-illustrator', 'adodb', 'adsi', 'adt',
            'advanced-search', 'advapi32', 'adventure', 'aero', 'aero-glass', 'aes', 'affinetransform', 'affinity',
            'after-effects', 'afx', 'aggregate', 'aggregate-functions', 'aggregate-initialization', 'aggregateroot',
            'aggregation', 'air', 'air-native-extension', 'aix', 'ajax', 'akka-zeromq', 'alchemy', 'alexa', 'algebra',
            'alglib', 'algorithm', 'aliasing', 'alignment', 'allegro', 'allegro5', 'alloc', 'alloca', 'allocation',
            'allocator', 'alpha', 'alpha-beta-pruning', 'alpha-transparency', 'alphabetical', 'alphablending',
            'alphanumeric', 'alsa', 'alt', 'alt-tab', 'always-on-top', 'amazon', 'amazon-s3', 'amazon-web-services',
            'ambiguity', 'ambiguous', 'ambiguous-call', 'amd-app', 'amd-processor', 'amplitude', 'amqp', 'anagram',
            'analog-digital-converter', 'analysis', 'analytics', 'analyzer', 'anchor', 'android', 'android-4.0',
            'android-4.2-jelly-bean', 'android-binder', 'android-canvas', 'android-library', 'android-logcat',
            'android-ndk', 'android-ndk-r5', 'android-sdcard', 'android-service', 'angelscript', 'angle', 'animation',
            'ankhsvn', 'annotations', 'anonymous', 'anonymous-class', 'anonymous-function', 'anonymous-pipes',
            'anonymous-struct', 'anonymous-types', 'ansi', 'ansi-c', 'ansistring', 'ant', 'anti-patterns', 'antivirus',
            'antlr', 'antlr3', 'aop', 'apache', 'apache2', 'apc', 'apdu', 'api', 'api-design', 'api-hook', 'app-config',
            'appcrash', 'appdomain', 'appearance', 'appkit', 'apple-push-notifications', 'applescript', 'appletviewer',
            'application-data', 'application-shutdown', 'application-structure', 'application-verifier',
            'apply-visitor', 'approximate', 'approximation', 'apr', 'apt', 'apxs2', 'aqtime', 'ar', 'ar.drone',
            'arbitrary-precision', 'arcgis', 'architecture', 'archive', 'arduino', 'area', 'argc', 'argouml',
            'argument-dependent-lookup', 'argument-passing', 'argv', 'arithmetic-expressions', 'arithmeticexception',
            'arm', 'armadillo', 'armv7', 'arp', 'arpack', 'array-initialization', 'array-initialize', 'arraylist',
            'arrays', 'artifacts', 'artificial-intelligence', 'artificial-life', 'artoolkit', 'ascii', 'ascii-art',
            'asihttprequest', 'aslr', 'asn.1', 'asp-classic', 'asp.net', 'asp.net-ajax', 'asp.net-mvc-4',
            'aspect-ratio', 'aspell', 'assemblies', 'assembly', 'assemblyinfo', 'assertion', 'assertions', 'assets',
            'assign', 'assignment-operator', 'assimp', 'associate', 'associative-array', 'asterisk',
            'asymptotic-complexity', 'async-workflow', 'asynchronous', 'asynchronously', 'asyncsocket', 'at-command',
            'atexit', 'ati', 'atl', 'atlas', 'atmel', 'atof', 'atoi', 'atomic-swap', 'atomicity', 'att', 'attributes',
            'audio', 'audio-panning', 'audio-processing', 'audio-recording', 'audio-streaming', 'audioeffect',
            'audiosession', 'audiounit', 'augmented-reality', 'authentication', 'authenticode', 'auto-build',
            'auto-generate', 'auto-increment', 'auto-indent', 'auto-ptr', 'auto-update', 'autocad', 'autocomplete',
            'autoconf', 'autodesk', 'autohotkey', 'autoload', 'automake', 'automata', 'automated-refactoring',
            'automated-tests', 'automatic-ref-counting', 'automation', 'automocking', 'autoplay', 'autorun',
            'autostart', 'autotools', 'avahi', 'avassetwriter', 'average', 'avi', 'avl-tree', 'avr', 'avr-gcc',
            'avrdude', 'avro', 'avx', 'awesomium', 'awk', 'awtrobot', 'axiom', 'axis', 'axis-labels', 'axis2', 'axis2c',
            'azure', 'azure-storage', 'azure-storage-blobs', 'azure-storage-queues', 'b-tree', 'background-color',
            'background-image', 'background-music', 'background-subtraction', 'backgroundworker', 'backlight',
            'backpropagation', 'backslash', 'backtrace', 'backtracking', 'backup', 'backwards-compatibility',
            'bad-alloc', 'bada', 'badimageformatexception', 'balloon', 'bandwidth', 'bank', 'barcode',
            'barcode-scanner', 'base-class', 'base-conversion', 'baseline', 'bash', 'bass', 'bass.dll', 'batch-file',
            'battery', 'baud-rate', 'bayesian', 'bbcode', 'bcd', 'bcp', 'bda', 'bdd', 'beagleboard', 'beam-search',
            'beep', 'beginthreadex', 'benchmarking', 'berkeley-db', 'berkeley-sockets', 'berkelium', 'best-fit-curve',
            'beta-distribution', 'bezier', 'bho', 'big-o', 'big5', 'bigint', 'biginteger', 'bignum', 'bimap',
            'bin-packing', 'binaries', 'binary', 'binary-compatibility', 'binary-data', 'binary-deserialization',
            'binary-heap', 'binary-search', 'binary-search-tree', 'binary-serialization', 'binary-tree', 'binaryfiles',
            'binaryreader', 'binarywriter', 'bind', 'bind2nd', 'binders', 'binomial-coefficients', 'binomial-heap',
            'binutils', 'bionic', 'bios', 'bipartite', 'birthday-paradox', 'bison', 'bit', 'bit-fields', 'bit-packing',
            'bit-shift', 'bitarray', 'bitblit', 'bitblt', 'bitboard', 'bitcount', 'bitflags', 'bitmap', 'bitmapimage',
            'bitmapsource', 'bitmask', 'bits', 'bitset', 'bitsets', 'bittorrent', 'bitvector', 'bitwise-and',
            'bitwise-operators', 'bitwise-or', 'bjam', 'blackberry', 'blackberry-10', 'blackberry-cascades',
            'blackberry-playbook', 'blackberry-qnx', 'blackjack', 'blank-line', 'blas', 'blend', 'blender', 'blending',
            'blit', 'blitz++', 'blobs', 'block', 'block-cipher', 'block-comments', 'blocking', 'blockingqueue', 'blogs',
            'bloom-filter', 'blowfish', 'bluetooth', 'bluetooth-lowenergy', 'blur', 'bmp', 'bnf', 'boggle',
            'boilerplate', 'bold', 'boolean-expression', 'boolean-logic', 'boolean-operations', 'boomerang', 'boost',
            'boost-any', 'boost-asio', 'boost-bind', 'boost-bjam', 'boost-build', 'boost-coroutine', 'boost-date-time',
            'boost-dynamic-bitset', 'boost-filesystem', 'boost-foreach', 'boost-format', 'boost-function',
            'boost-functional', 'boost-fusion', 'boost-geometry', 'boost-gil', 'boost-graph', 'boost-interprocess',
            'boost-iostreams', 'boost-iterators', 'boost-lambda', 'boost-locale', 'boost-log', 'boost-move',
            'boost-mpi', 'boost-mpl', 'boost-msm', 'boost-multi-array', 'boost-multi-index', 'boost-mutex',
            'boost-optional', 'boost-parameter', 'boost-phoenix', 'boost-polygon', 'boost-preprocessor',
            'boost-process', 'boost-program-options', 'boost-propertytree', 'boost-proto', 'boost-ptr-container',
            'boost-python', 'boost-random', 'boost-range', 'boost-ref', 'boost-regex', 'boost-serialization',
            'boost-signals', 'boost-signals2', 'boost-smart-ptr', 'boost-spirit', 'boost-spirit-karma',
            'boost-spirit-lex', 'boost-spirit-qi', 'boost-statechart', 'boost-test', 'boost-thread', 'boost-tokenizer',
            'boost-tuples', 'boost-ublas', 'boost-units', 'boost-unordered', 'boost-uuid', 'boost-variant',
            'boost-xpressive', 'boost.build', 'boot', 'bootloader', 'borland-c++', 'botan', 'bots', 'boundary',
            'bounding-box', 'bounds', 'bounds-checker', 'box2d', 'box2d-iphone', 'boxing', 'boxlayout', 'boxplot',
            'boyer-moore', 'bpl', 'brace-initialization', 'brackets', 'brainfuck', 'branch', 'branch-prediction',
            'branching-and-merging', 'breadth-first-search', 'breakpoints', 'bresenham', 'brew', 'brewmp', 'bridge',
            'brightness', 'broadband', 'broadcast', 'broker', 'browser', 'browser-cache', 'browser-plugin', 'brushes',
            'brute-force', 'bsd', 'bsearch', 'bsod', 'bson', 'bstr', 'bstr-t', 'bubble-sort', 'bucket-sort', 'buffer',
            'buffer-overflow', 'buffer-overrun', 'bufferedstream', 'buffering', 'bug-tracking', 'build',
            'build-automation', 'build-error', 'build-time', 'build-tools', 'builder', 'buildfarm', 'building',
            'buildroot', 'built-in', 'built-in-types', 'bulk', 'bulk-load', 'bulkinsert', 'bullet', 'bulletphysics',
            'bundle', 'bundler', 'bus', 'bus-error', 'busybox', 'button', 'byte-order-mark', 'bytearray', 'bytebuffer',
            'bytecode', 'bytecode-manipulation', 'bzip2', 'c', 'c++', 'c++-address', 'c++-amp', 'c++-concepts',
            'c++-cx', 'c++-faq', 'c++-tr2', 'c++03', 'c++11', 'c++14', 'c++17', 'c++98', 'c++builder',
            'c++builder-2007', 'c++builder-2009', 'c++builder-2010', 'c++builder-5', 'c++builder-6', 'c++builder-xe',
            'c++builder-xe2', 'c++builder-xe3', 'c-api', 'c-libraries', 'c-preprocessor', 'c-str', 'c-strings', 'c1001',
            'c11', 'c2664', 'c89', 'c99', 'caa', 'caching', 'cad', 'cairo', 'cakephp', 'cakephp-2.0', 'calc',
            'calculator', 'calendar', 'calibration', 'call', 'call-graph', 'callback', 'callbyname', 'callgrind',
            'calling-convention', 'calloc', 'callstack', 'camera', 'camera-calibration', 'cameracapturetask', 'can',
            'candidate', 'canonical-form', 'canvas', 'capitalization', 'captcha', 'caption', 'capture', 'car-analogy',
            'carbide', 'carchive', 'cardinality', 'cardspace', 'caret', 'cartesian', 'casablanca', 'cascade',
            'cascading', 'case-insensitive', 'cassandra', 'casting', 'casyncsocket', 'catch-all', 'category', 'catia',
            'cautoptr', 'cbc-mode', 'cbitmap', 'cbutton', 'cc', 'ccache', 'cclayer', 'ccmenuitem', 'ccombobox',
            'ccsprite', 'ccw', 'cd', 'cd-burning', 'cdash', 'cdb', 'cdc', 'cdecl', 'cdialog', 'cedet', 'cedit',
            'ceiklabel', 'ceil', 'cell', 'cellular-automata', 'centos', 'centos6', 'centroid', 'certificate', 'cfile',
            'cfiledialog', 'cfilefind', 'cfront', 'cfrunloop', 'cfstring', 'cg', 'cgal', 'cgbitmapcontext', 'cgi',
            'cgi-bin', 'cgimage', 'chain', 'chain-of-responsibility', 'chaining', 'channel', 'char-pointer', 'char16-t',
            'char32-t', 'character', 'character-arrays', 'character-encoding', 'chars', 'charsequence', 'charts',
            'chat', 'chatbot', 'chdir', 'checkbox', 'checkstyle', 'checksum', 'chess', 'chi-squared', 'chibios',
            'children', 'childwindow', 'chilkat', 'chinese-locale', 'chipmunk', 'chipset', 'chm', 'chop', 'chromakey',
            'chromium', 'chromium-embedded', 'chrono', 'chroot', 'cil', 'cilk-plus', 'cimg', 'cin', 'cinder', 'circle',
            'circuit', 'circular', 'circular-buffer', 'circular-dependency', 'circular-list', 'circular-reference',
            'cisco', 'citrix', 'cjk', 'clang', 'clang++', 'clang-complete', 'clang-static-analyzer',
            'class-constructors', 'class-design', 'class-diagram', 'class-library', 'class-members', 'class-method',
            'class-reference', 'class-structure', 'class-template', 'classification', 'classname', 'classwizard',
            'clear', 'click', 'clickonce', 'client', 'client-server', 'client-side', 'cliext', 'cling', 'clip',
            'clipboard', 'clipping', 'clips', 'clist', 'clistctrl', 'clock', 'clog', 'clojure', 'cloning', 'closures',
            'cloud', 'clr', 'clr-hosting', 'clrdump', 'clrs', 'clsid', 'clsidfromprogid', 'cluster-analysis',
            'cluster-computing', 'clutter', 'cmake', 'cmath', 'cmd', 'cmenu', 'cobol', 'cocoa', 'cocoa-bindings',
            'cocoa-touch', 'cocos2d-iphone', 'cocos2d-x', 'code-analysis', 'code-analyst', 'code-behind',
            'code-comments', 'code-completion', 'code-conversion', 'code-coverage', 'code-design', 'code-duplication',
            'code-formatting', 'code-generation', 'code-golf', 'code-injection', 'code-metrics', 'code-migration',
            'code-organization', 'code-reuse', 'code-review', 'code-separation', 'code-signing', 'code-size',
            'code-smell', 'code-snippets', 'code-timing', 'code-translation', 'codeblocks', 'codec', 'codecvt',
            'codegen', 'codehighlighter', 'codelite', 'codepages', 'codesourcery', 'codesynthesis', 'codewarrior',
            'coding-style', 'coercion', 'coldfusion', 'collaboration', 'collada', 'collapse', 'collation',
            'collections', 'collision', 'collision-detection', 'colon', 'color-palette', 'color-picker', 'colors',
            'column-sum', 'com', 'com+', 'com-interop', 'com-object', 'comaddin', 'combinations', 'combinatorics',
            'combobox', 'comeau', 'comet', 'comexception', 'comma', 'comma-operator', 'command', 'command-line',
            'command-line-arguments', 'command-line-interface', 'command-line-tool', 'command-pattern',
            'command-prompt', 'comments', 'common-controls', 'common-dialog', 'common-lisp', 'communication',
            'comobject', 'compact-database', 'compact-framework', 'compact-framework2.0', 'comparable', 'comparator',
            'compare', 'compare-and-swap', 'comparison', 'comparison-operators', 'compatibility', 'compilation',
            'compilation-time', 'compile-time', 'compile-time-constant', 'compiled', 'compiler-bug',
            'compiler-construction', 'compiler-development', 'compiler-errors', 'compiler-flags',
            'compiler-optimization', 'compiler-options', 'compiler-theory', 'compiler-warnings', 'compiz', 'complement',
            'complex-numbers', 'complexity-theory', 'components', 'composite', 'composition', 'compound-file',
            'compression', 'computation-theory', 'computational-geometry', 'compute-shader', 'computer-algebra-systems',
            'computer-architecture', 'computer-science', 'computer-vision', 'concatenation', 'concrt', 'concurrency',
            'concurrency-runtime', 'concurrent-programming', 'concurrenthashmap', 'condition', 'condition-variable',
            'conditional', 'conditional-breakpoint', 'conditional-compilation', 'conditional-operator',
            'conditional-statements', 'condor', 'config', 'configurability', 'configurable', 'configuration',
            'configuration-files', 'configuration-management', 'configurationmanager', 'configure', 'conflict',
            'conflicting-libraries', 'congestion-control', 'conio', 'connect', 'connection', 'connection-points',
            'connection-pooling', 'connection-string', 'connections', 'connectivity', 'connector', 'console',
            'console-application', 'const-cast', 'const-char', 'const-correctness', 'const-iterator', 'const-pointer',
            'const-reference', 'constantfolding', 'constants', 'constraints', 'construction', 'constructor-overloading',
            'consumer', 'contact', 'contain', 'container-managed', 'containers', 'containment', 'contains',
            'content-assist', 'contention', 'context-free-grammar', 'context-sensitive-grammar', 'context-switch',
            'context-switching', 'contextmenu', 'contiguous', 'continuous-integration', 'contour', 'contract',
            'control-flow', 'controller', 'controls', 'convention', 'conventions', 'conversion-operator', 'converter',
            'convex-hull', 'convolution', 'conways-game-of-life', 'cookies', 'coordinate-systems', 'coordinates',
            'copy-and-swap', 'copy-assignment', 'copy-constructor', 'copy-elision', 'copy-initialization',
            'copy-on-write', 'copy-paste', 'copy-protection', 'copying', 'copywithzone', 'corba', 'core', 'core-audio',
            'core-bluetooth', 'core-foundation', 'core-graphics', 'coredump', 'coroutine', 'correctness', 'corrupt',
            'corruption', 'cortex-m3', 'cos', 'cosine', 'count', 'countdown', 'counter', 'countif', 'counting',
            'coupling', 'cout', 'covariance', 'covariant', 'covariant-return-types', 'coverflow', 'coverity', 'cpack',
            'cpp-netlib', 'cppcheck', 'cppcms', 'cppdepend', 'cppunit', 'cpputest', 'cpropertysheet', 'cpu',
            'cpu-architecture', 'cpu-cache', 'cpu-cycles', 'cpu-registers', 'cpu-speed', 'cpu-usage', 'cpuid',
            'cpython', 'crash', 'crash-dumps', 'crash-reports', 'crashrpt', 'crc', 'crc32', 'create-guid',
            'createdibsection', 'createfile', 'createinstance', 'createprocess', 'createprocessasuser', 'createthread',
            'createuser', 'createwindowex', 'creation', 'credential-providers', 'credentials', 'cricheditctrl',
            'critical-section', 'cron', 'crop', 'cross-browser', 'cross-compiling', 'cross-language', 'cross-platform',
            'crosstool-ng', 'crossword', 'crt', 'crtdbg.h', 'crtp', 'cruisecontrol', 'cruisecontrol.net', 'cryengine',
            'crypto++', 'cryptoapi', 'cryptography', 'crystal-reports', 'crystal-space-3d', 'cscope', 'csplitterwnd',
            'css', 'css-position', 'cstdint', 'cstring', 'csv', 'ctabctrl', 'ctags', 'ctest', 'ctime',
            'ctor-initializer', 'ctp', 'ctrl', 'ctype', 'ctypes', 'cube', 'cubes', 'cubic', 'cublas', 'cucumber',
            'cucumber-cpp', 'cuda', 'cuda-gdb', 'cuda.net', 'culling', 'cunit', 'cups', 'curl', 'curlpp',
            'curly-braces', 'currency', 'current-dir', 'currying', 'curses', 'cursor', 'cursor-position', 'curve',
            'curve-fitting', 'cusp-library', 'custom-action', 'custom-component', 'custom-controls',
            'custom-error-handling', 'custom-error-pages', 'custom-exceptions', 'custom-type', 'custom-validators',
            'customization', 'cut', 'cvblobslib', 'cvs', 'cvv8', 'cwnd', 'cxxtest', 'cycle', 'cyclic',
            'cyclic-reference', 'cyclomatic-complexity', 'cygwin', 'cyk', 'cython', 'd', 'd-pointer', 'd3.js', 'd3dx',
            'dacl', 'daemon', 'dangling-pointer', 'darwin', 'data-access', 'data-access-layer', 'data-binding',
            'data-compression', 'data-conversion', 'data-driven', 'data-driven-tests', 'data-entry', 'data-fitting',
            'data-integrity', 'data-loss', 'data-manipulation', 'data-members', 'data-mining', 'data-modeling',
            'data-processing', 'data-protection', 'data-recovery', 'data-representation', 'data-sharing',
            'data-structures', 'data-transfer', 'data-visualization', 'database', 'database-connection',
            'database-design', 'database-template', 'dataflow', 'datagridview', 'datagridviewcheckboxcell',
            'datamember', 'dataset', 'datasource', 'datatable', 'date', 'date-arithmetic', 'date-conversion',
            'date-math', 'datetime', 'datetime-format', 'datetimepicker', 'dawg', 'db2', 'dbf', 'dbgeng', 'dbghelp',
            'dbi', 'dbunit', 'dbus', 'dbx', 'dcom', 'dct', 'ddd-debugger', 'dead-code', 'deadlock', 'deb', 'debian',
            'debug-build', 'debug-mode', 'debug-print', 'debug-symbols', 'debugbreak', 'debuggervisualizer',
            'debugging', 'debugview', 'decimal-point', 'declaration', 'declarative', 'declared-property', 'declspec',
            'decode', 'decoder', 'decoding', 'decompiler', 'decompiling', 'decompression', 'decorator', 'decouple',
            'decrease-key', 'decrement', 'deep-copy', 'default-arguments', 'default-constructor',
            'default-copy-constructor', 'default-parameters', 'default-value', 'defaulted-functions',
            'defaultlistmodel', 'defects', 'defensive-programming', 'deferred-rendering', 'deferred-shading',
            'definition', 'deflate', 'defragmentation', 'delay', 'delay-load', 'delayed-execution', 'delegates',
            'delegation', 'delete-directory', 'delete-file', 'delete-method', 'delete-operator', 'deleted-functions',
            'delimited-text', 'delimiter', 'delphi', 'delphi-2007', 'delphi-6', 'delphi-7', 'delphi-xe2', 'delphi-xe3',
            'denial-of-service', 'denied', 'denormalized', 'dep', 'dependencies', 'dependency-injection',
            'dependency-management', 'dependent-name', 'deploying', 'deployment', 'deprecated', 'depth', 'depth-buffer',
            'depth-first-search', 'deque', 'der', 'dereference', 'derivative', 'derived', 'derived-class',
            'derived-types', 'deriving', 'des', 'descriptor', 'deserialization', 'design', 'design-by-contract',
            'design-patterns', 'design-principles', 'design-rationale', 'designated-initializer', 'designer', 'desktop',
            'desktop-application', 'desktop-wallpaper', 'destruction', 'destructor', 'detect', 'detection',
            'determinants', 'deterministic', 'detours', 'dev-c++', 'dev-null', 'development-environment', 'device',
            'device-driver', 'device-emulation', 'deviceiocontrol', 'devil', 'devpartner', 'dft', 'dhcp', 'diacritics',
            'diagnostics', 'diagonal', 'diagram', 'dial-up', 'dialog', 'dialogbasedapp', 'diamond-problem', 'dib',
            'dice', 'dicom', 'dictionary', 'diff', 'differential-equations', 'digest', 'digit', 'digital-signature',
            'digits', 'digraphs', 'dijkstra', 'dimension', 'dimensional', 'dining-philosopher', 'direct2d', 'direct3d',
            'direct3d10', 'direct3d11', 'direct3d9', 'directdraw', 'directed-acyclic-graphs', 'directed-graph',
            'directfb', 'directinput', 'direction', 'directive', 'directory', 'directory-structure', 'directshow',
            'directshow.net', 'directsound', 'directwrite', 'directx', 'directx-10', 'directx-11', 'directx-9',
            'dirent.h', 'dirname', 'disable-caching', 'disassembly', 'disconnect', 'disconnected', 'discount',
            'disjoint-sets', 'disk', 'disk-partitioning', 'diskarbitration', 'diskspace', 'disparity-mapping',
            'dispatch', 'dispatcher', 'dispose', 'distance', 'distinguishedname', 'distortion', 'distribute',
            'distributed', 'distributed-algorithm', 'distributed-computing', 'distributed-system', 'distribution',
            'distro', 'distutils', 'divide-and-conquer', 'divide-by-zero', 'division', 'django', 'django-models',
            'djgpp', 'dll', 'dll-injection', 'dllexport', 'dllimport', 'dllnotfoundexception', 'dllregistration',
            'dlna', 'dlopen', 'dlsym', 'dma', 'dmalloc', 'dnf', 'dns', 'do-while', 'doc', 'dock', 'dockable', 'docking',
            'doctest', 'document', 'document-view', 'documentation', 'documentation-generation', 'documents', 'docview',
            'docx', 'dokan', 'dollar-sign', 'dom', 'domain-driven-design', 'domaincontroller', 'domdocument', 'dos',
            'dosbox', 'dot-operator', 'double-click', 'double-dispatch', 'double-free', 'double-pointer',
            'double-precision', 'double-underscore', 'doublebuffered', 'doubly-linked-list', 'downcast', 'downcasting',
            'download', 'doxygen', 'dpapi', 'dpi', 'drag-and-drop', 'draw', 'drawdib', 'drawellipse', 'drawing',
            'drawstring', 'drawtext', 'dreamweaver', 'drive', 'driver', 'drivers', 'drives', 'drm', 'drmaa',
            'drop-down-menu', 'dropbox', 'dropshadow', 'dry', 'dsl', 'dsn', 'dst', 'dtmf', 'dtrace', 'duffs-device',
            'dump', 'dumpbin', 'dumping', 'dup2', 'duplex', 'duplicate-data', 'duplicates', 'duplication', 'duration',
            'dvd', 'dvorak', 'dvr', 'dwarf', 'dwm', 'dword', 'dwt', 'dxgi', 'dyld', 'dylib', 'dynamic-allocation',
            'dynamic-arrays', 'dynamic-binding', 'dynamic-cast', 'dynamic-compilation', 'dynamic-data',
            'dynamic-languages', 'dynamic-library', 'dynamic-linking', 'dynamic-loading', 'dynamic-memory-allocation',
            'dynamic-programming', 'dynamic-proxy', 'dynamic-typing', 'dynamic-variables', 'dynamicobject', 'each',
            'easing', 'echo-server', 'eclipse', 'eclipse-3.4', 'eclipse-3.5', 'eclipse-cdt', 'eclipse-jdt',
            'eclipse-juno', 'eclipse-plugin', 'economics', 'edge', 'edge-detection', 'edit', 'edit-and-continue',
            'edit-control', 'editbox', 'editcontrol', 'editing', 'edsdk', 'eeprom', 'effect', 'effective-c++',
            'effects', 'efs', 'egl', 'eigen', 'eigenvalue', 'eintr', 'elasticsearch', 'electronics', 'element',
            'elements', 'elementwise-operations', 'elevation', 'elf', 'ellipsis', 'elliptic-curve', 'emacs',
            'emacs-semantic', 'email-client', 'email-integration', 'email-validation', 'embed', 'embedded',
            'embedded-browser', 'embedded-language', 'embedded-linux', 'embedded-resource', 'embedded-script',
            'embedded-sql', 'embedded-v8', 'embeddedwebserver', 'embedding', 'emgucv', 'emplace', 'empty-class',
            'emscripten', 'emulation', 'enable-if', 'encapsulation', 'encode', 'encoder', 'encoding', 'encryption',
            'encryption-asymmetric', 'end-of-line', 'endianness', 'endl', 'endpoint', 'ends-with', 'enter',
            'enterprise-architect', 'entity', 'entity-framework', 'entry-point', 'enum-class', 'enum-flags',
            'enumerable', 'enumerate', 'enumeration', 'enumerator', 'enums', 'envdte', 'envelope', 'environment',
            'environment-variables', 'enyo', 'eof', 'eol', 'epoch', 'epoll', 'eps', 'epsilon', 'equality', 'equals',
            'equals-operator', 'equation', 'equation-solving', 'equations', 'equivalence', 'equivalence-classes',
            'equivalent', 'erase', 'erase-remove-idiom', 'erlang', 'errno', 'error-checking', 'error-code',
            'error-correction', 'error-handling', 'error-logging', 'error-recovery', 'escaping', 'ethernet', 'etw',
            'euler-angles', 'evaluation', 'evc', 'evc4', 'event-driven', 'event-driven-design', 'event-handling',
            'event-hooking', 'event-log', 'event-loop', 'events', 'ewmh', 'exc-bad-access', 'excel', 'excel-2007',
            'excel-vba', 'exception', 'exception-handling', 'exception-safety', 'exception-specification',
            'exchange-server', 'exchangewebservices', 'exe', 'executable', 'execute', 'execution', 'execution-time',
            'execv', 'execvp', 'exi', 'exif', 'exists', 'exit-code', 'exit-handler', 'exitstatus', 'expand',
            'expansion', 'expat-parser', 'expect', 'expectation-maximization', 'expert-system', 'explicit-constructor',
            'explicit-conversion', 'explicit-instantiation', 'explicit-specialization', 'explode', 'explorer',
            'exponent', 'exponential', 'exponentiation', 'export-to-csv', 'express', 'expression',
            'expression-evaluation', 'expression-templates', 'expression-trees', 'extaudiofile', 'extend',
            'extended-ascii', 'extended-procedures', 'extending', 'extensibility', 'extension-methods', 'extern-c',
            'external', 'external-application', 'external-dependencies', 'external-process', 'external-sorting',
            'externals', 'extract', 'extraction', 'extraction-operator', 'extractor', 'exuberant-ctags', 'eye-tracking',
            'facade', 'face-detection', 'face-recognition', 'facebook', 'facet', 'factorial', 'factories', 'factoring',
            'factors', 'factory', 'factory-method', 'factory-pattern', 'fade', 'fading', 'fann', 'fastcall', 'fastcgi',
            'fastcgi++', 'fastformat', 'fastreport', 'fatal-error', 'fault', 'fault-tolerant-heap', 'fbo', 'fbx',
            'fcntl', 'feature-descriptor', 'feature-detection', 'feature-extraction', 'fedora', 'fedora16', 'feed',
            'feed-forward', 'feedback', 'feeds', 'feof', 'festival', 'ffi', 'fflush', 'ffmpeg', 'fft', 'fftw', 'fgetc',
            'fgetpos', 'fgets', 'fiber', 'fibers', 'fibonacci', 'fibonacci-heap', 'field', 'fifo', 'file-access',
            'file-comparison', 'file-conversion', 'file-copying', 'file-descriptor', 'file-extension', 'file-format',
            'file-handling', 'file-io', 'file-locking', 'file-management', 'file-mapping', 'file-monitoring',
            'file-organization', 'file-permissions', 'file-processing', 'file-read', 'file-recovery', 'file-rename',
            'file-search', 'file-sharing', 'file-storage', 'file-structure', 'file-transfer', 'file-upload', 'filebuf',
            'filechannel', 'filehandle', 'fileinfo', 'fileinputstream', 'fileloadexception', 'filemaker', 'filemap',
            'filenames', 'fileopendialog', 'fileoutputstream', 'fileparse', 'fileparsing', 'filepath', 'fileserver',
            'fileshare', 'filesize', 'filestream', 'filesystemobject', 'filesystems', 'filesystemwatcher', 'filetable',
            'fill', 'filter', 'filter-driver', 'filtering', 'finalizer', 'finance', 'find', 'findbugs', 'finder',
            'findwindow', 'findwindowex', 'fingerprint', 'finite-field', 'finite-state-machine', 'firebird',
            'firebreath', 'firefox', 'firefox-3', 'firefox-addon', 'firemonkey', 'firewall', 'firewire', 'firmware',
            'first-chance-exception', 'first-class', 'fix', 'fixed-length-record', 'fixed-point', 'fixed-size-types',
            'fixed-width', 'fizzbuzz', 'flags', 'flascc', 'flash', 'flash-media-server', 'flashdevelop', 'flashlite',
            'flat', 'flat-file', 'flex', 'flex++', 'flex-lexer', 'flexible-array-member', 'flicker', 'flip', 'floating',
            'floating-accuracy', 'floating-point', 'floating-point-conversion', 'floating-point-exceptions',
            'floating-point-precision', 'flock', 'flood-fill', 'floor', 'flops', 'flow', 'flow-control', 'flowlayout',
            'fltk', 'fluent-interface', 'flush', 'fmod', 'fmodf', 'focus', 'fold', 'folder', 'folder-structure',
            'folding', 'font-face', 'font-size', 'fontconfig', 'fonts', 'footprint', 'fop', 'fopen', 'for-loop',
            'force-based-algorithm', 'force-layout', 'fork', 'form-designer', 'formal-languages', 'format',
            'format-specifiers', 'format-string', 'formatmessage', 'formatted-input', 'formatted-text', 'formatting',
            'forms', 'formula', 'fortify', 'fortify-source', 'fortran', 'fortran-iso-c-binding', 'fortran77',
            'fortran90', 'fortran95', 'forward', 'forward-compatibility', 'forward-declaration', 'forward-list',
            'forwarding', 'forwarding-reference', 'fourcc', 'foxpro', 'fpic', 'fractals', 'fractions',
            'fragment-shader', 'fragmentation', 'frame', 'frame-rate', 'framebuffer', 'frames', 'frameworks', 'fread',
            'freak', 'free', 'free-function', 'freebsd', 'freeglut', 'freeimage', 'freertos', 'freetype', 'freetype2',
            'freeware', 'freeze-thaw', 'freopen', 'frequency', 'frequency-analysis', 'frequency-distribution',
            'friend-class', 'friend-function', 'frontend', 'frustum', 'fseek', 'fsevents', 'fsm', 'fstream', 'fsync',
            'ftdi', 'ftell', 'ftgl', 'ftp', 'ftp-server', 'full-text-search', 'fullscreen', 'function-attributes',
            'function-call', 'function-call-operator', 'function-calls', 'function-declaration', 'function-object',
            'function-overloading', 'function-overriding', 'function-parameter', 'function-pointers',
            'function-prototypes', 'function-signature', 'function-template', 'function-templates',
            'functional-programming', 'functor', 'future', 'future-proof', 'fuzzy-logic', 'fwrite', 'g++', 'g-wan',
            'g2log', 'galileo', 'galois-field', 'game-ai', 'game-development', 'game-engine', 'game-loop',
            'game-physics', 'game-theory', 'gamepad', 'ganymede', 'garbage-collection', 'gas', 'gate', 'gaussian',
            'gba', 'gcc', 'gcc-warning', 'gcc3', 'gcc4', 'gcc4.7', 'gcov', 'gd', 'gdal', 'gdb', 'gdbinit', 'gdbserver',
            'gdi', 'gdi+', 'gdk', 'gdkpixbuf', 'geany', 'gearman', 'gecko', 'gedit', 'gemfire', 'generated-code',
            'generator', 'generic-collections', 'generic-programming', 'generics', 'genetic', 'genetic-algorithm',
            'genetic-programming', 'genome', 'gentoo', 'geo', 'geocoding', 'geolocation', 'geometry',
            'geometry-surface', 'geos', 'geospatial', 'geotiff', 'gesture-recognition', 'getaddrinfo', 'getch',
            'getchar', 'getcwd', 'getdibits', 'getdirectories', 'getenv', 'getfileversion', 'gethostbyname',
            'getlasterror', 'getline', 'getmessage', 'getmodulefilename', 'getopenfilename', 'getopt', 'getopt-long',
            'getpixel', 'getprocaddress', 'getpwuid', 'getrusage', 'gets', 'getsystemmetrics', 'getter',
            'getter-setter', 'gettext', 'getusermedia', 'gfortran', 'ghostdoc', 'gif', 'gil', 'gina', 'ginac', 'gis',
            'git', 'git-diff', 'githooks', 'github', 'giza++', 'gl-triangle-strip', 'glade', 'gldrawpixels', 'glew',
            'glfw', 'glib', 'glibc', 'glibmm', 'glload', 'glm-math', 'glob', 'global-namespace', 'global-scope',
            'global-variables', 'globalization', 'glog', 'glow', 'glowcode', 'glpk', 'glreadpixels', 'glsl',
            'glteximage2d', 'glu', 'glulookat', 'glut', 'glutcreatewindow', 'glx', 'gmail', 'gmock', 'gmp', 'gnome',
            'gnome-3', 'gnome-shell', 'gnome-shell-extensions', 'gnome-terminal', 'gnu', 'gnu-coreutils', 'gnu-make',
            'gnu-toolchain', 'gnuplot', 'gnuradio', 'gnutls', 'go-to-definition', 'gobject', 'gobject-introspection',
            'god-object', 'gomoku', 'google-books', 'google-calendar', 'google-chrome', 'google-chrome-frame',
            'google-ctemplate', 'google-drive-sdk', 'google-earth', 'google-earth-plugin', 'google-gears',
            'google-maps', 'google-maps-api-3', 'google-nativeclient', 'google-perftools', 'google-search',
            'google-style-guide', 'google-visualization', 'googlemock', 'googletest', 'gouraud', 'gperf', 'gperftools',
            'gpgpu', 'gpio', 'gpl', 'gpo', 'gprof', 'gprs', 'gps', 'gpsd', 'gpu', 'gpu-programming', 'grails',
            'grammar', 'grand-central-dispatch', 'graph', 'graph-algorithm', 'graph-databases', 'graph-theory',
            'graph-traversal', 'graphedit', 'graphic', 'graphical-programming', 'graphics', 'graphics2d',
            'graphicsmagick', 'graphing', 'graphviz', 'grayscale', 'greatest-common-divisor', 'greedy', 'greenhills',
            'gregorian-calendar', 'grep', 'grid', 'grid-computing', 'grid-layout', 'gridview', 'groovy', 'group-policy',
            'groupbox', 'grouping', 'gsl', 'gsm', 'gsoap', 'gson', 'gssapi', 'gstreamer', 'gtk', 'gtk3', 'gtkmm',
            'gtktreeview', 'gui-designer', 'gui-toolkit', 'guid', 'gunzip', 'gwt-history', 'gz', 'gzip', 'gzipstream',
            'h.264', 'haar-wavelet', 'hadoop', 'hal', 'halide', 'halo', 'hamiltonian-cycle', 'hamming-code',
            'hamming-numbers', 'hamsterdb', 'handle', 'handle-leak', 'handler', 'handles', 'hang', 'hard-coding',
            'hard-drive', 'hardcode', 'hardware', 'hardware-id', 'hardware-interface', 'hardy-ramanujan', 'hash',
            'hash-collision', 'hash-function', 'hashalgorithm', 'hashcode', 'hashmap', 'hashset', 'hashtable',
            'haskell', 'haversine', 'haxe', 'hbitmap', 'hdc', 'hdf5', 'hdmi', 'hdrimages', 'header', 'header-files',
            'header-only', 'headless-browser', 'headphones', 'headset', 'heap', 'heap-corruption', 'heap-fragmentation',
            'heap-memory', 'heap-randomization', 'heapalloc', 'heapsort', 'heartbeat', 'heisenbug', 'helper',
            'heterogeneous', 'heterogeneous-services', 'hex', 'hex-editors', 'hexdump', 'hibernate', 'hid',
            'hidden-features', 'hidden-files', 'hide', 'hiding', 'hierarchical', 'hierarchy', 'high-availability',
            'high-resolution', 'higher-order-functions', 'highlighting', 'hindi', 'hiphop', 'hiredis', 'histogram',
            'historical-debugging', 'history', 'hittest', 'hlsl', 'hmac', 'hmacsha1', 'hoisting', 'hole-punching',
            'homebrew', 'homescreen', 'homography', 'hook', 'host', 'hosted', 'hosting', 'hosts', 'hotfix', 'hotkeys',
            'hough-transform', 'hover', 'hp-ux', 'hpc', 'hpet', 'hresult', 'hsl', 'hsv', 'html-agility-pack',
            'html-content-extraction', 'html-escape', 'html-parsing', 'html5', 'htonl', 'http', 'http-authentication',
            'http-chunked', 'http-get', 'http-headers', 'http-post', 'http-redirect', 'http-request', 'httpd.conf',
            'httprequest', 'https', 'httpserver', 'httpwebrequest', 'hud', 'hudson', 'huffman-code', 'hung',
            'hungarian-notation', 'hwnd', 'hyper-v', 'hyperlink', 'hypertable', 'i2c', 'i386', 'ia-32', 'iar', 'ibm-mq',
            'icalendar', 'icc', 'icccm', 'icloud', 'icmp', 'icons', 'iconv', 'icu', 'id3', 'id3v2', 'ida', 'ide',
            'identification', 'identifier', 'identity', 'idioms', 'idispatch', 'idl', 'idn', 'ieee', 'ieee-754',
            'ienumerable', 'if-statement', 'ifndef', 'ifstream', 'ignore', 'ihtmldocument2', 'iis', 'iis-6', 'iis-7',
            'iis-7.5', 'ijg', 'il', 'illegal-input', 'imacros', 'image', 'image-capture', 'image-conversion',
            'image-formats', 'image-manipulation', 'image-processing', 'image-recognition', 'image-resizing',
            'image-rotation', 'image-scaling', 'image-scanner', 'image-segmentation', 'image-size', 'image-stitching',
            'imageflow', 'imagelist', 'imagemagick', 'imagemagick-convert', 'imaging', 'imap', 'imdb', 'ime',
            'immutability', 'imperative-programming', 'impersonation', 'implementation', 'implicit-cast',
            'implicit-conversion', 'import-from-csv', 'importerror', 'in-class-initialization', 'in-memory',
            'in-memory-database', 'in-place', 'include-guards', 'include-path', 'inclusion', 'incompatibility',
            'incomplete-type', 'incredibuild', 'increment', 'incremental-linking', 'indentation', 'indesign', 'indexer',
            'indexing', 'indexoutofboundsexception', 'indices', 'indirection', 'indy', 'indy10', 'inequality', 'inet',
            'inet-ntop', 'inet-socket', 'inetd', 'infiniband', 'infinite', 'infinite-loop', 'infinity',
            'infix-notation', 'inflate', 'inflection', 'info-hash', 'infopath', 'information-extraction',
            'information-hiding', 'information-retrieval', 'informix', 'inheritance', 'ini', 'initialization',
            'initialization-list', 'initialization-order', 'initialization-vector', 'initializer', 'initializer-list',
            'inject', 'inline-assembly', 'inline-functions', 'inline-method', 'inlining', 'inner-classes',
            'inner-exception', 'inno-setup', 'innovation', 'inode', 'inorder', 'inotify', 'input', 'input-devices',
            'inputstream', 'insert', 'insert-iterator', 'insertion', 'insertion-order', 'insertion-sort', 'install',
            'installation', 'installer', 'installshield', 'instance', 'instance-variables', 'instant-messaging',
            'instantiation', 'instruction-set', 'instructions', 'instrumentation', 'instruments', 'integer',
            'integer-arithmetic', 'integer-division', 'integer-hashing', 'integer-overflow', 'integer-promotion',
            'integral', 'integrate', 'integration', 'integration-testing', 'integrity', 'intel', 'intel-inspector',
            'intel-ipp', 'intel-mkl', 'intel-pin', 'intellij-idea', 'intellisense', 'intellitrace',
            'inter-process-communicat', 'interaction', 'interactive', 'interbase', 'interface-design',
            'interface-implementation', 'interlocked', 'interlocked-increment', 'internals', 'internationalization',
            'internet-connection', 'internet-explorer', 'internet-explorer-6', 'internet-explorer-7',
            'internet-explorer-8', 'internet-explorer-9', 'interop', 'interpolation', 'interpreted-language',
            'interpreter', 'interprocess', 'interrupt', 'intersection', 'interval-intersection', 'interval-tree',
            'intervals', 'intptr', 'intraweb', 'intrinsics', 'introsort', 'introspection', 'intrusive-containers',
            'invalid-argument', 'invalidate', 'invariants', 'inventory', 'inverse', 'inversion', 'inversion-of-control',
            'invert', 'invocation', 'invoke', 'io', 'io-buffering', 'io-completion-ports', 'io-redirection', 'iocp',
            'ioctl', 'iokit', 'iomanip', 'ios', 'ios-simulator', 'ios4', 'ios5', 'ios6', 'iostream', 'ip', 'ip-address',
            'ip-protocol', 'ipad', 'ipc', 'ipconfig', 'iphelper', 'iphone', 'iplimage', 'ipopt', 'iptables', 'ipv4',
            'ipv6', 'iris-recognition', 'irix', 'irrlicht', 'is-empty', 'isapi', 'isapi-extension', 'isapi-redirect',
            'isnullorempty', 'iso', 'iso-8859-1', 'iso9660', 'isometric', 'istorage', 'istream', 'istream-iterator',
            'istringstream', 'itanium', 'iterable', 'iterable-unpacking', 'iteration', 'iterator', 'iterator-traits',
            'itertools', 'itextsharp', 'itk', 'itoa', 'iunknown', 'iwebbrowser2', 'ixmldomdocument', 'ixmldomelement',
            'ixmldomnode', 'jack', 'jagged-arrays', 'jam', 'jar', 'java', 'java-access-bridge', 'java-ee', 'java-me',
            'javacpp', 'javacv', 'javadoc', 'javafx-2', 'javah', 'javascript', 'jenkins', 'jenkins-plugins', 'jffs2',
            'jgrasp', 'jint', 'jit', 'jms', 'jmx', 'jna', 'jni', 'jnienv', 'jniwrapper', 'job-scheduling', 'jobs',
            'jogl', 'josephus', 'journaling', 'jpeg', 'jpeg-xr', 'jpeg2000', 'jquery', 'jscript', 'json', 'json-rpc',
            'jsoncpp', 'jsoniq', 'jsp', 'jstack', 'jta', 'juce', 'julian', 'jump-list', 'jump-table', 'junit', 'jvm',
            'jvm-arguments', 'jvm-crash', 'k-means', 'kadanes-algorithm', 'kalman-filter', 'kbhit', 'kcachegrind',
            'kconfig', 'kde', 'kdelibs', 'kdevelop', 'kdevelop4', 'kdtree', 'keil', 'kerberos', 'kernel', 'kernel-mode',
            'kernel-module', 'kerning', 'key', 'key-bindings', 'key-value', 'key-value-observing', 'keyboard',
            'keyboard-events', 'keyboard-hook', 'keyboard-input', 'keyboard-shortcuts', 'keycode', 'keydown',
            'keyevent', 'keylistener', 'keylogger', 'keypoint', 'keypress', 'keyset', 'keystroke', 'keyup', 'keyword',
            'kill', 'kill-process', 'kinect', 'kinect-sdk', 'kissfft', 'kmdf', 'kml', 'knapsack-problem', 'knn',
            'knuth', 'kparts', 'kruskals-algorithm', 'ksh', 'kubuntu', 'kyotocabinet', 'l-systems', 'label', 'labview',
            'lag', 'lame', 'lan', 'lang', 'language-agnostic', 'language-binding', 'language-comparisons',
            'language-construct', 'language-design', 'language-details', 'language-detection', 'language-extension',
            'language-features', 'language-implementation', 'language-interoperability', 'language-lawyer',
            'language-switching', 'language-translation', 'lapack', 'lapack++', 'large-data', 'large-data-volumes',
            'large-file-support', 'large-files', 'largenumber', 'last.fm', 'lastindexof', 'late-binding', 'latency',
            'latex', 'latin', 'latin1', 'latitude-longitude', 'launch', 'launch-time', 'launchd', 'launcher',
            'law-of-demeter', 'layer', 'layered-windows', 'layout', 'layout-manager', 'lazy-c++', 'lazy-evaluation',
            'lazy-initialization', 'lazy-loading', 'lcd', 'lcov', 'lcs', 'ld', 'ld-preload', 'ldap', 'ldf',
            'least-squares', 'led', 'leda', 'legacy', 'legacy-code', 'legend', 'lego', 'lemmatization',
            'lemon-graph-library', 'less', 'letters', 'levenberg-marquardt', 'levenshtein-distance', 'lex', 'lexer',
            'lexical', 'lexical-analysis', 'lexical-cast', 'lexical-closures', 'lexical-scope', 'lexicographic', 'lgpl',
            'libav', 'libavcodec', 'libavformat', 'libc', 'libc++', 'libclang', 'libconfig', 'libcurl', 'libdc1394',
            'libev', 'libevent', 'libffi', 'libharu', 'libjingle', 'libjpeg', 'libjson', 'liblacewing', 'libm',
            'libmysql', 'libnds', 'libopc', 'libpcap', 'libpng', 'libpq', 'libpqxx', 'libqxt', 'libraries',
            'library-design', 'libreoffice', 'librocket', 'librsync', 'libs', 'libsigc++', 'libsndfile',
            'libspatialindex', 'libssh', 'libssh2', 'libssl', 'libstdc++', 'libtiff', 'libtool', 'libtorrent', 'libusb',
            'libusb-1.0', 'libuv', 'libvirt', 'libx264', 'libxml2', 'license-key', 'licensing', 'lifecycle', 'lifetime',
            'lighting', 'lighttpd', 'limit', 'limits', 'line-breaks', 'line-count', 'line-endings', 'line-numbers',
            'line-processing', 'line-segment', 'linear', 'linear-algebra', 'linear-equation', 'linear-interpolation',
            'linear-programming', 'linear-regression', 'lines', 'lines-of-code', 'linkage', 'linked-list', 'linker',
            'linker-errors', 'linker-scripts', 'linker-warning', 'linq', 'lint', 'linux', 'linux-device-driver',
            'linux-kernel', 'linuxmint', 'lisp', 'list-initialization', 'listbox', 'listcontrol', 'listen', 'listener',
            'listview', 'literals', 'literate-programming', 'live', 'live555', 'lldb', 'llvm', 'llvm-3.0',
            'llvm-c++-api', 'llvm-clang', 'llvm-gcc', 'llvm-ir', 'lnk', 'lnk2001', 'lnk2005', 'lnk2019', 'lnk2022',
            'load', 'load-balancing', 'loader', 'loaderlock', 'loadimage', 'loading', 'loadlibrary', 'local',
            'local-network', 'local-variables', 'locale', 'localhost', 'localityofreference', 'localization',
            'localserver', 'localtime', 'location', 'lock-free', 'locking', 'log4cplus', 'log4cpp', 'log4cxx', 'log4j',
            'logfiles', 'logging', 'logic', 'logical-operators', 'login', 'logitech', 'logoff', 'logout', 'loki',
            'long-double', 'long-filenames', 'long-integer', 'longest-substring', 'longjmp', 'lookahead', 'lookaround',
            'lookbehind', 'lookup', 'lookup-tables', 'loop-unrolling', 'looper', 'loops', 'lossless-compression',
            'lostfocus', 'lotus', 'lotus-domino', 'lotus-notes', 'low-latency', 'low-level', 'low-memory',
            'lower-bound', 'lowercase', 'lparam', 'lpbyte', 'lpcstr', 'lpcwstr', 'lpstr', 'lptstr', 'lr', 'lru', 'ls',
            'lto', 'ltrace', 'lua', 'lua-5.2', 'lua-api', 'lua-c++-connection', 'lua-table', 'luabind', 'lucene',
            'lucene.net', 'luhn', 'lvalue', 'lwjgl', 'lzma', 'lzw', 'm4a', 'mac-address', 'mach-o', 'machine-code',
            'machine-learning', 'machine-translation', 'macos', 'macos-carbon', 'macports', 'macrodef', 'macros',
            'maemo', 'magic-numbers', 'magic-square', 'magick++', 'magnification-api', 'mahjong', 'mailslot', 'main',
            'mainframe', 'maintainability', 'maintenance', 'make-shared', 'makefile', 'makefile-project', 'malloc',
            'man', 'managed', 'managed-c++', 'managed-code', 'managed-extensions', 'mandelbrot', 'manifest',
            'manipulators', 'mapi', 'mapisendmail', 'maple', 'mapping', 'mapreduce', 'maps', 'markdown', 'markov',
            'marmalade', 'mars-simulator', 'mask', 'masm', 'massif', 'master-detail', 'master-slave', 'master-theorem',
            'mat', 'matcher', 'matchevaluator', 'matching', 'material', 'math', 'math.h', 'mathematica-8',
            'mathematical-morphology', 'mathematical-optimization', 'mathgl', 'mathlink', 'mathprog', 'matlab',
            'matlab-compiler', 'matlab-cvst', 'matlab-deployment', 'matlab-engine', 'matrix', 'matrix-factorization',
            'matrix-inverse', 'matrix-multiplication', 'matrix-vision', 'maven', 'maven-2', 'maven-nar-plugin',
            'maven-plugin', 'max', 'max-flow', 'max-path', 'max-size', 'maya', 'maze', 'mbcs', 'mbed', 'mcafee', 'mci',
            'mcisendstring', 'mcmc', 'md5', 'md5sum', 'mdd', 'mdi', 'mdp', 'mean', 'measure', 'measurement', 'media',
            'median', 'mediawiki', 'meego', 'mel', 'member', 'member-access', 'member-function-pointers',
            'member-initialization', 'member-pointers', 'member-variables', 'members', 'memcached', 'memcheck',
            'memcmp', 'memcpy', 'memmove', 'memoization', 'memory', 'memory-address', 'memory-alignment',
            'memory-barriers', 'memory-consumption', 'memory-corruption', 'memory-dump', 'memory-efficient',
            'memory-fences', 'memory-fragmentation', 'memory-layout', 'memory-leak-detector', 'memory-leaks',
            'memory-limit', 'memory-management', 'memory-mapped-files', 'memory-mapping', 'memory-model',
            'memory-optimization', 'memory-pool', 'memory-profiling', 'memorystream', 'memset', 'menu', 'menubar',
            'menuitem', 'mercurial', 'merge', 'mergesort', 'mersenne-twister', 'mesh', 'message', 'message-loop',
            'message-passing', 'message-pump', 'message-queue', 'messagebox', 'messagepack', 'messaging', 'metaclass',
            'metadata', 'metafile', 'metaio', 'metaobject', 'metaprogramming', 'metatable', 'metatrader4', 'meteor',
            'method-chaining', 'method-hiding', 'method-names', 'method-overloading', 'method-signature', 'methodology',
            'methods', 'metric', 'metrics', 'metrowerks', 'mex', 'mfc', 'mfc-feature-pack', 'mfc-networking',
            'micro-optimization', 'microblaze', 'microchip', 'microcontroller', 'microphone', 'microprocessors',
            'microsoft-dynamics', 'microsoft-glee', 'microsoft-metro', 'microsoft-runtime-library', 'middleware',
            'midi', 'midl', 'mifare', 'miglayout', 'migradoc', 'migration', 'milliseconds', 'mime', 'min', 'min-heap',
            'mindstorms', 'minecraft', 'minesweeper', 'mingw', 'mingw-w64', 'mingw32', 'mini-xml', 'minidump',
            'minifilter', 'minimax', 'minimum', 'mint', 'mipmaps', 'mips', 'mips32', 'mismatch', 'misra',
            'mission-critical', 'mit-scratch', 'mitk', 'mixed', 'mixed-code', 'mixed-mode', 'mixer', 'mixing', 'mixins',
            'mjpeg', 'mkdir', 'mkfifo', 'mkstemp', 'mktime', 'mkv', 'mmap', 'mmc', 'mmu', 'mnemonics', 'mnist',
            'mobile', 'mobile-emulator', 'mobile-phones', 'mocking', 'mod-pagespeed', 'modal-dialog', 'modbus', 'mode',
            'model', 'model-view', 'model-view-controller', 'modeless', 'modeling', 'modular', 'modular-arithmetic',
            'modularity', 'modulo', 'modulus', 'monads', 'mongo-cxx-driver', 'mongodb', 'mongodb-c',
            'mongoose-web-server', 'monitor', 'mono', 'monodevelop', 'monostate', 'montage', 'montecarlo',
            'monthcalendar', 'moose', 'moses', 'most-vexing-parse', 'mosync', 'motherboard', 'motif', 'motion',
            'motion-detection', 'motordriver', 'mount', 'mount-point', 'mouse', 'mouse-hook', 'mouseclick-event',
            'mouseevent', 'mouseover', 'movable', 'move', 'move-assignment-operator', 'move-constructor',
            'move-semantics', 'moving-average', 'mozilla', 'mp3', 'mp4', 'mpc', 'mpeg', 'mpeg-4', 'mpeg2-ts', 'mpfr',
            'mpi', 'mpich', 'mql4', 'mqueue', 'ms-access', 'ms-access-2007', 'ms-media-foundation', 'ms-office',
            'ms-project', 'ms-word', 'msbuild', 'msdn', 'msgpack', 'mshtml', 'msmq', 'msn', 'mstest', 'msvcr90.dll',
            'msvcrt', 'msxml', 'msxml3', 'msxml4', 'msxml6', 'msys', 'mt', 'mtom', 'mtp', 'mtu', 'mui', 'multi-index',
            'multi-level', 'multi-touch', 'multibyte', 'multicast', 'multicore', 'multidimensional-array', 'multifile',
            'multilanguage', 'multiline', 'multimap', 'multimedia', 'multipart', 'multipass', 'multiple-columns',
            'multiple-definition-error', 'multiple-gpu', 'multiple-inclusions', 'multiple-inheritance',
            'multiple-languages', 'multiple-monitors', 'multiple-processes', 'multiple-projects', 'multiplestacks',
            'multiplexing', 'multiplication', 'multiprocess', 'multiprocessing', 'multiset', 'multitasking',
            'multitexturing', 'multithreading', 'multiway-tree', 'murmurhash', 'music', 'mutability', 'mutators',
            'mutex', 'mutual-recursion', 'mvcc', 'mvvm', 'myisam', 'mysql', 'mysql++', 'mysql-connector',
            'mysql-error-1062', 'mysql4', 'mysqlpp', 'n-queens', 'n73', 'name-clash', 'name-decoration', 'name-hiding',
            'name-lookup', 'name-mangling', 'named', 'named-constructor', 'named-parameters', 'named-pipes', 'names',
            'namespaces', 'naming', 'naming-conventions', 'nan', 'nano', 'nant', 'narrowing', 'nas', 'nasm', 'nat',
            'nat-traversal', 'native-code', 'native-methods', 'natural-sort', 'naudio', 'navigation', 'ncbi', 'ncr',
            'ncurses', 'ndef', 'ndepend', 'ndis', 'nearest-neighbor', 'negation', 'negative-number', 'neon', 'nested',
            'nested-class', 'nested-loops', 'net-snmp', 'netapp', 'netbeans', 'netbeans-6.9', 'netbeans-7',
            'netbeans-7.2', 'netbeans-plugins', 'netbeans6.7', 'netburner', 'netfilter', 'netflow', 'netlink', 'netsh',
            'netstat', 'netty', 'network-interface', 'network-printers', 'network-programming', 'network-protocols',
            'network-security', 'networking', 'neural-network', 'new-operator', 'newline', 'newtons-method', 'nexus-4',
            'nexus-7', 'nfc', 'nfs', 'nginx', 'nic', 'nightly-build', 'nintendo', 'nintendo-ds', 'nio', 'nlopt', 'nltk',
            'nmake', 'nmap', 'nmea', 'nmf', 'nntp', 'no-match', 'node-gyp', 'node.js', 'nodes', 'nohup',
            'noise-generator', 'nokia', 'nomenclature', 'non-alphanumeric', 'non-deterministic', 'non-greedy',
            'non-member-functions', 'non-recursive', 'non-static', 'non-type', 'non-unicode',
            'non-uniform-distribution', 'non-virtual-interface', 'non-volatile', 'nonblocking', 'nonclient',
            'noncopyable', 'nonlinear-optimization', 'noop', 'normal-distribution', 'normalization', 'normalize',
            'normals', 'nosql', 'nosuchmethoderror', 'notation', 'notepad', 'notepad++', 'nothrow', 'notifications',
            'notifyicon', 'noweb', 'npapi', 'npm', 'npp', 'nrvo', 'ns2', 'nsarray', 'nsarraycontroller', 'nsdata',
            'nsfilemanager', 'nsight', 'nsimage', 'nsis', 'nslock', 'nsnotificationcenter', 'nsoperation',
            'nsoperationqueue', 'nsstring', 'nstimer', 'nsurl', 'nsurlconnection', 'nsurlrequest', 'nt-native-api',
            'ntdll', 'ntfs', 'ntfs-mft', 'ntl', 'ntlm', 'ntp', 'ntvdm', 'nui', 'null-character', 'null-pointer',
            'null-terminated', 'nullpointerexception', 'nullreferenceexception', 'numa', 'number-formatting',
            'number-rounding', 'number-theory', 'numbers', 'numeric', 'numeric-limits', 'numeric-ranges', 'numerical',
            'numerical-analysis', 'numerical-integration', 'numerical-methods', 'numerical-stability', 'numpy', 'nunit',
            'nvarchar', 'nvcc', 'nvidia', 'nvprof', 'nvvp', 'nxt', 'oauth', 'obfuscation', 'objdump',
            'object-composition', 'object-construction', 'object-design', 'object-destruction', 'object-detection',
            'object-files', 'object-lifetime', 'object-oriented-analysis', 'object-pooling', 'object-recognition',
            'object-reference', 'object-slicing', 'objectarx', 'objectfactory', 'objective-c', 'objective-c++',
            'objective-c-blocks', 'objective-c-runtime', 'observer-pattern', 'ocaml', 'occi', 'occlusion', 'oci', 'ocr',
            'octal', 'octave', 'octest', 'octree', 'ocx', 'odb', 'odb-orm', 'odbc', 'ode', 'ode-library', 'odeint',
            'off-by-one', 'office-automation', 'offline', 'offset', 'offsetof', 'ofnhookproc', 'ofstream', 'ofx', 'ogg',
            'oggvorbis', 'ogre', 'ogre3d', 'oid', 'ole', 'oledb', 'omake', 'omap', 'omnet++', 'omnicomplete', 'on-disk',
            'onclick', 'ondemand', 'ondrawitem', 'one-definition-rule', 'one-time-password', 'one-to-many', 'onkeydown',
            'onkillfocus', 'onmouseover', 'onncpaint', 'onpaint', 'onpause', 'onunload', 'onvif', 'ooad', 'oolua',
            'oop', 'opacity', 'opaque-pointers', 'opcode', 'opcodes', 'open-source', 'openacc', 'openal', 'opencl',
            'opencv', 'openfiledialog', 'openframeworks', 'opengl', 'opengl-2.0', 'opengl-3', 'opengl-4', 'opengl-es',
            'opengl-es-1.1', 'opengl-es-2.0', 'opengl-to-opengles', 'openglcontext', 'openkinect', 'openmax', 'openmp',
            'openmpi', 'openni', 'openoffice.org', 'openprocess', 'openscenegraph', 'openssl', 'openstreetmap',
            'opensuse', 'openvms', 'openxml', 'opera', 'operand', 'operands', 'operating-system', 'operation',
            'operations', 'operator-keyword', 'operator-overloading', 'operator-precedence', 'operators', 'opos',
            'oprofile', 'optical-drive', 'optical-mark-recognition', 'opticalflow', 'optimization', 'optimizer-hints',
            'option', 'optional', 'optional-arguments', 'optional-parameters', 'options', 'opus', 'or-operator',
            'ora-00001', 'ora-28002', 'oracle', 'oracle-pro-c', 'oracle10g', 'oracle11g', 'orbacus', 'order',
            'order-of-evaluation', 'ordinals', 'organization', 'orientation', 'orm', 'os-agnostic', 'os.execl', 'osc',
            'osdev', 'osgi', 'osi', 'ostream', 'ostringstream', 'osx-lion', 'osx-mountain-lion', 'osx-snow-leopard',
            'otl', 'out-of-memory', 'out-of-process', 'out-parameters', 'outer-join', 'outlook', 'outlook-2003',
            'outlook-addin', 'outofrangeexception', 'output', 'output-parameter', 'outputstream', 'overflow',
            'overhead', 'overlap', 'overlapped-io', 'overlay', 'overload-resolution', 'overloading', 'overrides',
            'overwrite', 'owl', 'ownerdrawn', 'ownership', 'ownership-semantics', 'p', 'p2p', 'pack',
            'package-managers', 'packaged-task', 'packages', 'packaging', 'packet', 'packet-capture', 'packet-loss',
            'packet-sniffers', 'packets', 'packing', 'padding', 'page-replacement', 'pagefile', 'pageheap',
            'pagination', 'paging', 'paint', 'paintevent', 'pair', 'pairing-heap', 'palette', 'palindrome', 'palm',
            'palm-os', 'pam', 'panda3d', 'pandaboard', 'pane', 'panel', 'pango', 'panoramas', 'pantheios', 'paradigms',
            'parallax', 'parallel-for', 'parallel-port', 'parallel-processing', 'param', 'parameter-passing',
            'parameterization', 'parameterized', 'parameters', 'params-keyword', 'parasoft', 'pardiso', 'parent-child',
            'parentheses', 'parse-error', 'parser-generator', 'parsing', 'partial-application', 'partial-classes',
            'partial-ordering', 'partial-specialization', 'particle-filter', 'particle-system', 'partitioning',
            'pascal', 'pascals-triangle', 'pass-by-const-reference', 'pass-by-pointer', 'pass-by-reference',
            'pass-by-rvalue-reference', 'pass-by-value', 'passthru', 'password-encryption', 'password-protection',
            'password-recovery', 'passwords', 'paste', 'pastebin', 'patch', 'path', 'path-finding', 'path-variables',
            'pathing', 'patricia-trie', 'pattern-matching', 'pattern-recognition', 'payload', 'paypal', 'pbkdf2', 'pbo',
            'pc-lint', 'pca', 'pcap', 'pch', 'pci-bus', 'pclose', 'pcm', 'pcre', 'pcx', 'pda', 'pdb', 'pdb-files',
            'pdcurses', 'pdf', 'pdf-generation', 'pdfview', 'pdk', 'pearson', 'peek', 'pem', 'percent-encoding',
            'percentage', 'percentile', 'perf', 'perfect-forwarding', 'perfect-numbers', 'perfect-square', 'perfmon',
            'perforce', 'performance', 'performance-testing', 'performancecounter', 'perl', 'perlin-noise', 'perltk',
            'permissions', 'permutation', 'persistence', 'persistent-data', 'persistent-storage', 'personalization',
            'perspective', 'perspectivecamera', 'perspectives', 'petsc', 'pf-ring', 'pgi', 'pgm', 'pgo', 'phonon',
            'photon', 'photoshop', 'php', 'php-extension', 'php-internals', 'phpmyadmin', 'physfs', 'physical-design',
            'physics', 'physics-engine', 'physx', 'pi', 'pic', 'picker', 'picking', 'pickle', 'picturebox', 'pid',
            'pimpl-idiom', 'ping', 'pinvoke', 'pion-net', 'pipe', 'pipeline', 'pipelining', 'pitch', 'pitch-tracking',
            'pivot', 'pixel', 'pixelate', 'pixels', 'pixmap', 'pjsip', 'pkg-config', 'placeholder', 'placement-new',
            'plagiarism-detection', 'plane', 'planerotation', 'platform', 'platform-builder', 'platform-independent',
            'platform-sdk', 'platform-specific', 'playback', 'player', 'playing-cards', 'playsound', 'playstation',
            'playstation-portable', 'plesk', 'plot', 'plpgsql', 'plugins', 'pmd', 'png', 'png-24', 'pocketpc', 'poco',
            'poco-libraries', 'pod', 'podofo', 'point', 'point-cloud-library', 'point-clouds', 'pointer-arithmetic',
            'pointer-container', 'pointer-conversion', 'pointer-to-member', 'pointers', 'points', 'poisson', 'poker',
            'polarssl', 'policy', 'policy-based-design', 'policy-injection', 'polling', 'polygon', 'polyline',
            'polymorphism', 'polynomial-math', 'polyvariadic', 'pong', 'pool', 'pop', 'popen', 'poppler', 'popup',
            'popup-balloons', 'port', 'portability', 'portable-executable', 'portaudio', 'portforwarding', 'porting',
            'ports', 'pose-estimation', 'posix', 'posix-api', 'post', 'post-build-event', 'post-increment',
            'post-processing', 'postfix-notation', 'postfix-operator', 'postgresql', 'postgresql-9.1', 'postgresql-9.2',
            'postmessage', 'postmortem-debugging', 'postorder', 'pow', 'power-law', 'power-management', 'powerpc',
            'powerpoint', 'powerset', 'powershell', 'ppi', 'ppl', 'ppm', 'ppp', 'pppoe', 'praat', 'pragma', 'prc-tools',
            'pre-build-event', 'pre-increment', 'precision', 'precompile', 'precompiled-headers', 'preconditions',
            'predicate', 'preferences', 'prefetch', 'prefix-operator', 'premature-optimization', 'preorder', 'prepare',
            'prepared-statement', 'preprocessor', 'preprocessor-directive', 'pretty-print', 'preview',
            'prime-factoring', 'primes', 'primitive', 'primitive-types', 'prims-algorithm', 'principles',
            'print-preview', 'printer-properties', 'printf', 'printing', 'printk', 'priority-queue',
            'private-constructor', 'private-key', 'private-members', 'privilege', 'privilege-elevation', 'privileges',
            'prng', 'probability', 'probe', 'proc', 'procedural', 'procedural-generation', 'procedural-programming',
            'procedure', 'process', 'process-elevation', 'process-explorer', 'process-management',
            'process-substitution', 'processing', 'processing-efficiency', 'processor', 'processors', 'procfs',
            'producer', 'producer-consumer', 'product', 'production', 'productivity-power-tools', 'profile', 'profiler',
            'profiling', 'program-slicing', 'program-transformation', 'programming-languages', 'progress',
            'progress-bar', 'project', 'project-files', 'project-management', 'project-organization',
            'project-planning', 'projectile', 'projection', 'projection-matrix', 'projector', 'projects',
            'projects-and-solutions', 'prolog', 'promise', 'promotions', 'properties', 'propertyeditor', 'propertygrid',
            'propertysheet', 'protection', 'protein-database', 'protobuf-net', 'protocol-buffers', 'protocol-handler',
            'protocols', 'protostuff', 'prototype', 'prototyping', 'proxy', 'proxy-authentication', 'proxy-classes',
            'proxy-pattern', 'ps3', 'pseudocode', 'pspsdk', 'psql', 'psse', 'pst', 'pthread-join', 'pthreads',
            'ptr-vector', 'ptrace', 'ptx', 'pty', 'public-fields', 'public-key', 'public-key-encryption', 'publish',
            'publish-subscribe', 'pugixml', 'pulseaudio', 'pure-virtual', 'purely-functional', 'purify', 'push-back',
            'pushdown-automaton', 'put', 'putty', 'puzzle', 'pvs-studio', 'py++', 'pybindgen', 'pycuda', 'pyd',
            'pygame', 'pyinstaller', 'pymunk', 'pyobject', 'pyopengl', 'pyqt', 'pyqt4', 'pyside', 'pythagorean',
            'python', 'python-2.6', 'python-2.7', 'python-3.3', 'python-3.x', 'python-bindings', 'python-c-api',
            'python-c-extension', 'python-embedding', 'python-idle', 'python-imaging-library', 'python-sip',
            'python-sphinx', 'qabstractitemmodel', 'qabstractlistmodel', 'qabstracttablemodel', 'qapplication',
            'qbasic', 'qbytearray', 'qcar-sdk', 'qchar', 'qcheckbox', 'qcombobox', 'qdbus', 'qdebug', 'qdialog', 'qdir',
            'qdjango', 'qdockwidget', 'qemu', 'qevent', 'qfile', 'qfiledialog', 'qfilesystemmodel',
            'qfilesystemwatcher', 'qgis', 'qglwidget', 'qgraphicsitem', 'qgraphicsscene', 'qgraphicsview',
            'qgridlayout', 'qhash', 'qi', 'qicon', 'qimage', 'qitemdelegate', 'qjson', 'qkeyevent', 'qlabel', 'qlayout',
            'qlikview', 'qlineedit', 'qlist', 'qlistview', 'qlistwidget', 'qlocalsocket', 'qmail', 'qmainwindow',
            'qmake', 'qmap', 'qmdiarea', 'qmediaplayer', 'qmenu', 'qmessagebox', 'qml', 'qnetworkaccessmanager', 'qnx',
            'qnx-neutrino', 'qobject', 'qpainter', 'qpixmap', 'qplaintextedit', 'qpointer', 'qprocess', 'qprogressbar',
            'qpushbutton', 'qr-code', 'qregexp', 'qscrollarea', 'qsettings', 'qshareddata', 'qsharedpointer', 'qslider',
            'qsort', 'qsortfilterproxymodel', 'qspinbox', 'qsplitter', 'qsqlquery', 'qsqltablemodel', 'qss',
            'qsslsocket', 'qstandarditemmodel', 'qstatemachine', 'qstring', 'qstyleditemdelegate', 'qstylesheet', 'qt',
            'qt-creator', 'qt-designer', 'qt-events', 'qt-installer', 'qt-jambi', 'qt-mfc-migration', 'qt-necessitas',
            'qt-quick', 'qt-resource', 'qt-signals', 'qt3', 'qt4', 'qt4.7', 'qt4.8', 'qt5', 'qtabbar', 'qtableview',
            'qtablewidget', 'qtablewidgetitem', 'qtabwidget', 'qtconcurrent', 'qtcore', 'qtcpserver', 'qtcpsocket',
            'qtembedded', 'qtestlib', 'qtextcursor', 'qtextdocument', 'qtextedit', 'qtgui', 'qthread', 'qtimer',
            'qtkit', 'qtnetwork', 'qtoolbar', 'qtp', 'qtquick2', 'qtreeview', 'qtreewidget', 'qtreewidgetitem',
            'qtscript', 'qtserialport', 'qtsql', 'qtwebkit', 'quad', 'quadratic', 'quadtree', 'qualifiers', 'quantlib',
            'quantum-computing', 'quartz-graphics', 'quaternions', 'quazip', 'query-notifications', 'queue',
            'quickbooks', 'quickfix', 'quicksort', 'quicktime', 'quotes', 'quoting', 'qurl', 'qvariant', 'qwebkit',
            'qwebpage', 'qwebview', 'qwidget', 'qwindow', 'qwt', 'qx11embedcontainer', 'r', 'r-tree', 'rabbitmq',
            'race-condition', 'rad', 'radio-button', 'radix', 'radix-sort', 'ragel', 'raii', 'rake', 'raknet', 'ram',
            'ram-scraping', 'ramdisk', 'random', 'random-access', 'random-forest', 'random-seed', 'random-testing',
            'range-tree', 'ranking', 'rapi', 'rapidjson', 'rapidxml', 'raspberry-pi', 'raspbian', 'rasterizing', 'rate',
            'ratio', 'rational-numbers', 'rational-rose', 'raw-ethernet', 'raw-input', 'raw-pointer', 'raw-sockets',
            'ray', 'ray-picking', 'raycasting', 'raytracing', 'rbac', 'rc', 'rcf', 'rcpp', 'rcs', 'rcw', 'rdbms',
            'rdoc', 'rdp', 'rdrand', 'rdtsc', 'react-os', 'read-eval-print-loop', 'read-write', 'readability',
            'readdir', 'readdirectorychangesw', 'readelf', 'readerwriterlock', 'readfile', 'readline',
            'readprocessmemory', 'real-time', 'real-time-data', 'realloc', 'realview', 'reboot', 'recent-file-list',
            'recipe', 'recompile', 'record', 'records', 'recordset', 'recovery', 'rectangles', 'recurrence',
            'recurring', 'recursion', 'recursive-datastructures', 'recursive-descent', 'recursive-mutex', 'recv',
            'recycle-bin', 'red-black-tree', 'redefinition', 'redhat', 'redirect', 'redis', 'redistributable',
            'redundancy', 'reentrant', 'refactoring', 'refcounting', 'reference', 'reference-counting',
            'reference-type', 'reference-wrapper', 'reflection', 'reflector', 'reformat', 'refresh', 'regasm', 'regex',
            'region', 'register-allocation', 'registry', 'registrykey', 'regression', 'regression-testing', 'regsvr32',
            'reinterpret-cast', 'relational', 'relationship', 'relative-path', 'release', 'release-builds',
            'release-mode', 'reload', 'remote-access', 'remote-debugging', 'remote-desktop', 'remote-process',
            'remoting', 'removable-drive', 'remove-if', 'removing-whitespace', 'rename', 'render', 'render-to-texture',
            'renderer', 'rendering', 'rendering-engine', 'rendertarget', 'repaint', 'repetition', 'replace',
            'replication', 'reporting', 'repository', 'repository-design', 'repr', 'representation', 'request',
            'rescale', 'reserved-words', 'reset', 'reshape', 'resharper', 'resize', 'resolution', 'resolver',
            'resource-cleanup', 'resource-dll', 'resource-files', 'resource-leak', 'resource-management',
            'resourcemanager', 'resources', 'rest', 'restart', 'restrict-qualifier', 'restriction', 'restsharp',
            'result', 'result-of', 'resultset', 'resume', 'return-by-reference', 'return-by-value', 'return-path',
            'return-type', 'return-value', 'return-value-optimization', 'reusability', 'reuters', 'reverse',
            'reverse-iterator', 'reversing', 'rfc', 'rfc3339', 'rfcomm', 'rfid', 'rgb', 'rgba', 'rhapsody', 'rhel5',
            'rhel6', 'ribbon', 'rich-text-editor', 'richedit', 'richedit-control', 'richtext', 'richtextbox', 'rights',
            'rigid-bodies', 'rijndael', 'rijndaelmanaged', 'rinside', 'roaming-profile', 'robotics', 'robust',
            'robustness', 'rogue-wave', 'roguelike', 'rollover', 'rom', 'roman-numerals', 'root', 'root-framework',
            'rope', 'ropes', 'ros', 'rotatetransform', 'rotation', 'rotational-matrices', 'rounded-corners', 'rounding',
            'rounding-error', 'roundtrip', 'router', 'routing', 'row', 'rpc', 'rpn', 'rs485', 'rsa',
            'rsacryptoserviceprovider', 'rstudio', 'rsync', 'rsyslog', 'rtaudio', 'rtd', 'rte', 'rtf', 'rtmp', 'rtos',
            'rtp', 'rtsp', 'rtti', 'rubiks-cube', 'ruby', 'ruby-c-extension', 'ruby-on-rails', 'rubymotion',
            'rule-engine', 'rule-of-three', 'rules', 'run-length-encoding', 'runas', 'running-other-programs',
            'runtime', 'runtime-error', 'runtime-type', 'runtime.exec', 'runtimeexception', 'rusage', 'rust', 'rvalue',
            'rvalue-reference', 'rvo', 's60', 'safari', 'safearray', 'sal', 'sample', 'samplegrabber', 'sampling',
            'samsung-mobile', 'samsung-smart-tv', 'sandbox', 'sanitization', 'sapi', 'sat-solvers', 'save', 'save-as',
            'savefiledialog', 'saving-data', 'sax', 'saxparser', 'scala', 'scalability', 'scalable', 'scalapack',
            'scalar', 'scale', 'scan-build', 'scancodes', 'scanf', 'scanline', 'scanning', 'scatter', 'scatter-plot',
            'scene', 'scenegraph', 'scheduled-tasks', 'scheduler', 'scheduling', 'schema', 'scheme',
            'scientific-computing', 'scientific-notation', 'scilab', 'scintilla', 'scipy', 'sco-unix', 'scons', 'scope',
            'scope-resolution', 'scoped-lock', 'scoped-ptr', 'scopeguard', 'scopes', 'scoping', 'scp', 'screen',
            'screen-capture', 'screen-resolution', 'screen-scraping', 'screensaver', 'screenshot', 'scripting',
            'scripting-language', 'scroll', 'scrollbar', 'scrollview', 'scsi', 'sd-card', 'sdk', 'sdl', 'sdl-1.2',
            'sdl-2', 'sdl-image', 'sdl-mixer', 'sdl-ttf', 'seam', 'search', 'search-engine', 'secondlife', 'sections',
            'sector', 'securid', 'security', 'security-roles', 'sed', 'seed', 'seeding', 'seek', 'seekg', 'segment',
            'segment-tree', 'segmentation-fault', 'segments', 'seh', 'select-function', 'selection', 'selectlist',
            'selectnodes', 'selector', 'self-destruction', 'self-extracting', 'self-modifying', 'self-organizing-maps',
            'semantics', 'semaphore', 'semicolon', 'send', 'sendfile', 'sendinput', 'sendkeys', 'sendmessage', 'sendto',
            'sentence', 'sentinel', 'separation-of-concerns', 'separator', 'seqan', 'sequence', 'sequence-points',
            'sequences', 'sequential', 'serial-communication', 'serial-number', 'serial-port', 'serialization',
            'server-administration', 'server-hardware', 'server-push', 'server-side', 'serversocket', 'service',
            'service-locator', 'servicecontroller', 'servlets', 'session', 'sessionid', 'set-difference',
            'set-intersection', 'set-union', 'setattribute', 'setf', 'setfocus', 'setjmp', 'setsockopt', 'setter',
            'setthreadaffinitymask', 'settings', 'setuid', 'setup-deployment', 'setvalue', 'setw', 'setwindowshookex',
            'sfinae', 'sfml', 'sftp', 'sgi', 'sha', 'sha1', 'sha256', 'shadow', 'shadow-copy', 'shadow-mapping',
            'shadows', 'shallow-copy', 'shape', 'shapes', 'share', 'shared', 'shared-libraries', 'shared-memory',
            'shared-objects', 'shared-ptr', 'sharepoint', 'shareware', 'sharing', 'sharpdx', 'shedskin', 'shell',
            'shell-exec', 'shell-extensions', 'shell-icons', 'shell32', 'shellexecute', 'shfileoperation', 'shockwave',
            'short-circuiting', 'shortcut', 'shortcuts', 'shortest-path', 'shorthand', 'show', 'show-hide',
            'showdialog', 'showwindow', 'shrink', 'shuffle', 'shunting-yard', 'shutdown', 'sid', 'side-by-side',
            'side-effects', 'sidebar', 'siebel', 'sieve', 'sieve-of-eratosthenes', 'sift', 'sig-atomic-t', 'sigabrt',
            'sigar', 'sigbus', 'sigchld', 'sigfpe', 'sigint', 'sigkill', 'sign', 'signal-handling', 'signal-processing',
            'signals', 'signals-slots', 'signals2', 'signature', 'signedness', 'signing', 'sigpipe', 'sigsegv',
            'sigterm', 'silverlight', 'simd', 'similarity', 'simple-machines-forum', 'simplehttpserver', 'simplify',
            'simulate', 'simulated-annealing', 'simulation', 'simulator', 'simulink', 'simultaneous', 'sin',
            'singleton', 'singly-linked-list', 'singular', 'sip', 'size-t', 'size-type', 'skeletal-mesh', 'skin',
            'skinning', 'skins', 'skip', 'skip-lists', 'skybox', 'skype', 'skype4com', 'skype4java', 'skype4py',
            'slam-algorithm', 'sleep', 'sli', 'slice', 'slickedit', 'slider', 'slot', 'slots', 'smart-pointers',
            'smart-tv', 'smartcard', 'smartphone', 'smarty', 'smo', 'smoothing', 'smp', 'sms', 'smtp', 'sniffing',
            'snmp', 'snmp-trap', 'soa', 'soap', 'soci', 'socket.io', 'socketchannel', 'sockets', 'socks',
            'soft-input-panel', 'soft-keyboard', 'software-design', 'software-distribution', 'software-packaging',
            'software-product-lines', 'soil', 'solaris', 'solaris-10', 'solid-bodies', 'solution', 'solution-explorer',
            'solver', 'som', 'sonarqube', 'sorted', 'sorting', 'soundex', 'soundpool', 'source-code-protection',
            'source-insight', 'sox', 'space', 'space-partitioning', 'spaces', 'spacing', 'spam', 'spam-prevention',
            'sparc', 'sparse-file', 'sparse-matrix', 'spatial', 'spatial-index', 'spatial-query', 'spawn', 'spawning',
            'special-characters', 'specialization', 'specifications', 'specifier', 'spectrogram', 'spectrum', 'speech',
            'speech-recognition', 'speech-synthesis', 'speex', 'spell-checking', 'sphinx', 'spi', 'spidermonkey',
            'spinlock', 'spinning', 'splash', 'splash-screen', 'splay-tree', 'splice', 'spline', 'splines', 'split',
            'splitter', 'spotify', 'sprite', 'sprite-sheet', 'spritebatch', 'spritefont', 'sprof', 'spy++', 'sql',
            'sql-server', 'sql-server-2000', 'sql-server-2005', 'sql-server-2005-express', 'sql-server-2008',
            'sql-server-2008-r2', 'sql-server-ce', 'sqlbindparameter', 'sqlcipher', 'sqlconnection', 'sqldmo', 'sqlite',
            'sqlite3', 'sqlncli', 'sqrt', 'sqsh', 'square', 'square-bracket', 'square-root', 'squeak', 'squirrel',
            'srand', 'src', 'sse', 'sse2', 'sse3', 'sse4', 'ssh', 'ssl', 'ssl-certificate', 'sslhandshakeexception',
            'sslstream', 'sspi', 'sstream', 'stability', 'stable-sort', 'stack', 'stack-based', 'stack-dump',
            'stack-memory', 'stack-overflow', 'stack-pointer', 'stack-size', 'stack-smash', 'stack-trace',
            'stack-unwinding', 'stackframe', 'stackunderflow', 'staff-wsf', 'stan', 'standard-deviation',
            'standard-error', 'standard-layout', 'standard-library', 'standards', 'standards-compliance', 'standby',
            'startmenu', 'startup', 'stat', 'stata', 'state', 'state-machines', 'statechart', 'states', 'statet',
            'static-analysis', 'static-array', 'static-assert', 'static-cast', 'static-code-analysis',
            'static-constructor', 'static-data', 'static-initialization', 'static-libraries', 'static-linking',
            'static-members', 'static-methods', 'static-order-fiasco', 'static-polymorphism', 'static-typing',
            'static-variables', 'static-visitor', 'statistics', 'status', 'status-register', 'statusbar', 'std',
            'std-function', 'std-pair', 'stdafx.h', 'stdasync', 'stdatomic', 'stdbind', 'stdcall', 'stdclass', 'stderr',
            'stdhash', 'stdin', 'stdint', 'stdio', 'stdlist', 'stdmap', 'stdmove', 'stdout', 'stdset', 'stdstring',
            'stdthread', 'stdtuple', 'stdvector', 'steganography', 'stencil-buffer', 'step-into', 'stereo-3d',
            'stereoscopy', 'stingray', 'stl', 'stl-algorithm', 'stlmap', 'stlport', 'stm32', 'stocks', 'storage',
            'storage-class-specifier', 'store', 'stored-procedures', 'str-replace', 'strassen', 'strategy-pattern',
            'strcat', 'strcat-s', 'strchr', 'strcmp', 'strcpy', 'strdup', 'stream', 'stream-operators', 'streambuf',
            'streaming', 'streamreader', 'streamwriter', 'stretch', 'stretchdibits', 'strftime', 'strict-aliasing',
            'strict-weak-ordering', 'string-building', 'string-comparison', 'string-concatenation', 'string-conversion',
            'string-formatting', 'string-interning', 'string-length', 'string-literals', 'string-matching',
            'string-parsing', 'string-search', 'string-table', 'string.format', 'string.h', 'stringbuffer',
            'stringification', 'stringio', 'stringstream', 'stringtokenizer', 'strip', 'strncmp', 'strncpy',
            'strong-typing', 'strongname', 'strpos', 'strsafe', 'strstream', 'strtok', 'strtol',
            'struct-member-alignment', 'struct-vs-class', 'struct.pack', 'structure', 'structure-packing',
            'structured-exception', 'structured-storage', 'stub', 'stx', 'stxxl', 'styles', 'stylesheet', 'styling',
            'stylus-pen', 'sub-array', 'subclass', 'subclassing', 'subdirectories', 'subdirectory', 'subfolder',
            'sublimetext', 'sublimetext2', 'submatrix', 'submenu', 'subprocess', 'subscript-operator', 'subset',
            'subset-sum', 'subst', 'substr', 'substring', 'subtitle', 'subtract', 'subtraction', 'subtype', 'sudo',
            'sudoku', 'suffix-array', 'suffix-tree', 'suid', 'suitesparse', 'sum', 'sum-of-digits', 'sun', 'suncc',
            'sungridengine', 'sunos', 'sunrpc', 'sunstudio', 'superblock', 'superclass', 'superscript', 'superset',
            'suppress', 'suppress-warnings', 'surf', 'surface', 'suse', 'suspend', 'svd', 'svg', 'svm', 'svn', 'swap',
            'swi-prolog', 'swig', 'swing', 'switch-statement', 'switching', 'swizzling', 'sxs', 'sybase-asa', 'symbian',
            'symbol', 'symbol-table', 'symbolic-math', 'symbols', 'symlink', 'symmetric', 'sympy', 'sync',
            'synchronization', 'synchronous', 'syntactic-sugar', 'syntastic', 'syntax', 'syntax-error',
            'syntax-highlighting', 'synthesis', 'synthesizer', 'sys', 'sysinternals', 'syslistview32', 'syslog',
            'system', 'system-calls', 'system-error', 'system-font', 'system-testing', 'system-tray', 'system-verilog',
            'system.net', 'systemc', 'systems-programming', 'systemtime', 'systray', 'systypes.h', 't4',
            'tab-delimited-text', 'tabbed-interface', 'tabbed-view', 'tabcontrol', 'tablecolumn', 'tablet', 'tablet-pc',
            'tableview', 'tabs', 'tabview', 'taglib', 'tags', 'tail', 'tail-call-optimization', 'tail-recursion', 'tao',
            'tao-framework', 'tap', 'tapi', 'tar', 'target', 'task', 'task-parallel-library', 'task-queue', 'taskbar',
            'taskmanager', 'tasm', 'tbb', 'tcc', 'tchar', 'tcl', 'tcl-api', 'tclientdataset', 'tcmalloc', 'tcp',
            'tcp-ip', 'tcp-port', 'tcpclient', 'tcpdump', 'tcplistener', 'tcpserver', 'tdatetime', 'tdd', 'tdm-mingw',
            'teamcity', 'tee', 'teechart', 'tegra', 'telephony', 'telnet', 'temperature', 'template-aliases',
            'template-classes', 'template-deduction', 'template-engine', 'template-function', 'template-matching',
            'template-meta-programming', 'template-method-pattern', 'template-mixins', 'template-specialization',
            'template-templates', 'templates', 'templates-deduction', 'temporary', 'temporary-files',
            'temporary-objects', 'terminal', 'terminal-services', 'terminate', 'terminate-handler', 'termination',
            'terminology', 'termios', 'ternary', 'ternary-operator', 'ternary-search-tree', 'ternary-tree', 'terrain',
            'tesselation', 'tessellation', 'tesseract', 'testability', 'testcase', 'testing', 'testing-strategies',
            'tethering', 'tex', 'text', 'text-alignment', 'text-based', 'text-editor', 'text-files', 'text-parsing',
            'text-processing', 'text-rendering', 'text-segmentation', 'text-to-speech', 'textbox', 'textfield',
            'textinput', 'textmate', 'texture-mapping', 'texture2d', 'textures', 'tfs', 'tfsbuild', 'tftp', 'tga',
            'themes', 'theming', 'theory', 'thermal-printer', 'this-pointer', 'thoughtworks-go', 'thread-exceptions',
            'thread-local', 'thread-local-storage', 'thread-priority', 'thread-safety', 'thread-state',
            'thread-synchronization', 'threadabortexception', 'threadgroup', 'threadpool', 'thrift', 'throttle',
            'throttling', 'throughput', 'throwable', 'thrust', 'thumbnails', 'thunderbird', 'thunk', 'tic-tac-toe',
            'tiff', 'tile', 'tile-engine', 'tiles', 'tiling', 'timage', 'time', 'time-complexity', 'time-format',
            'time-series', 'time-t', 'time-trial', 'time.h', 'timedelta', 'timeout', 'timer', 'timespec', 'timestamp',
            'timezone', 'timezoneoffset', 'timing', 'tinyxml', 'tinyxml++', 'tinyxml2', 'titlebar', 'tk', 'tkinter',
            'tlbimp', 'tlv', 'tmemo', 'toast', 'todo', 'token', 'tokenize', 'tokyo-cabinet', 'tolower', 'toolbar',
            'toolbars', 'toolbox', 'toolchain', 'toolkit', 'tooltip', 'topmost', 'topography', 'torque', 'tortoisesvn',
            'tostring', 'touch', 'touch-event', 'touchscreen', 'towers-of-hanoi', 'tr1', 'tr2', 'tr24731', 'trac',
            'trace', 'tracing', 'trackball', 'trackbar', 'tracker', 'tracking', 'trackpopupmenu', 'tradeoff', 'trading',
            'trailing-return-type', 'traits', 'transactional-memory', 'transactions', 'transfer', 'transform',
            'transformation', 'transition', 'translate', 'translate-animation', 'translation', 'transliteration',
            'transparency', 'transparent', 'transport', 'transport-stream', 'transpose', 'traveling-salesman',
            'traversal', 'travis-ci', 'tray', 'trayicon', 'tree', 'tree-balancing', 'tree-traversal', 'treemodel',
            'treenode', 'treeview', 'treewidget', 'trello', 'trial', 'trialware', 'triangle-count', 'triangular',
            'triangulation', 'trichedit', 'trie', 'trigonometry', 'trigraphs', 'trim', 'trinitycore', 'true-type-fonts',
            'truncate', 'truncation', 'try-catch', 'try-catch-finally', 'tsql', 'tuples', 'turbo-c', 'turbo-c++',
            'turing-complete', 'twain', 'twebbrowser', 'twilio', 'twitter', 'twitter-oauth', 'twos-complement',
            'type-conversion', 'type-deduction', 'type-erasure', 'type-inference', 'type-library', 'type-mismatch',
            'type-punning', 'type-safety', 'type-systems', 'type-theory', 'typecast-operator', 'typechecking',
            'typeconverter', 'typeerror', 'typeinfo', 'typelib', 'typelist', 'types', 'typetraits', 'typing',
            'typography', 'u-boot', 'uac', 'ublas', 'ubuntu', 'ubuntu-10.04', 'ubuntu-10.10', 'ubuntu-11.04',
            'ubuntu-11.10', 'ubuntu-12.04', 'ubuntu-12.10', 'ubuntu-8.10', 'ubuntu-9.04', 'ubuntu-unity', 'uclibc',
            'uclinux', 'ucs', 'ucs2', 'udp', 'udpclient', 'ui-design', 'ui-thread', 'uiimage', 'uiimageview', 'uilabel',
            'uima', 'uint32-t', 'uint8t', 'uipi', 'uitableview', 'ultimategrid', 'umdf', 'umdh', 'umfpack', 'uml',
            'uname', 'unary-function', 'unary-operator', 'unboxing', 'unbuffered', 'unc', 'uncaught-exception',
            'uncrustify', 'undeclared-identifier', 'undefined', 'undefined-behavior', 'undefined-reference',
            'undefined-symbol', 'underflow', 'underscores', 'undo', 'undo-redo', 'undocumented-behavior', 'unhandled',
            'unhandled-exception', 'unicode', 'unicode-normalization', 'unicode-string', 'uniform-initialization',
            'uninstall', 'unions', 'unique', 'unique-id', 'unique-ptr', 'uniqueidentifier', 'unistd.h',
            'unit-conversion', 'unit-testing', 'units-of-measurement', 'unittest++', 'unity3d', 'universal-binary',
            'universal-reference', 'universalindentgui', 'unix', 'unix-socket', 'unix-timestamp', 'unlink', 'unlock',
            'unmanaged', 'unmanaged-memory', 'unmarshalling', 'unnamed-namespace', 'unordered', 'unordered-map',
            'unordered-set', 'unpack', 'unresolved-external', 'unsafe-pointers', 'unsatisfiedlinkerror',
            'unsigned-char', 'unsigned-integer', 'unsigned-long-long-int', 'unspecified-behavior', 'unused-variables',
            'unzip', 'upcasting', 'updates', 'updating', 'upgrade', 'upload', 'upnp', 'uppercase', 'upx', 'uri', 'url',
            'url-encoding', 'url-rewriting', 'url-scheme', 'urldecode', 'urlencode', 'urlmon', 'usability',
            'usage-statistics', 'usagepatterns', 'usb', 'usb-drive', 'usb-flash-drive', 'usbserial', 'use-case',
            'user-accounts', 'user-activity', 'user-agent', 'user-controls', 'user-defined-functions',
            'user-defined-literals', 'user-input', 'user-interaction', 'user-interface', 'user32', 'usergroups',
            'using-declaration', 'using-directives', 'using-statement', 'usleep', 'uss', 'utc', 'utf', 'utf-16',
            'utf-8', 'utilities', 'utility', 'utilization', 'uuid', 'uv-mapping', 'uxtheme', 'v4l2', 'v8', 'valarray',
            'valgrind', 'validation', 'value-type', 'valuestack', 'varchar', 'variable-address', 'variable-assignment',
            'variable-declaration', 'variable-initialization', 'variable-length', 'variable-length-array', 'variables',
            'variadic', 'variadic-functions', 'variadic-macros', 'variadic-templates', 'variant', 'vb.net', 'vb6',
            'vba', 'vbo', 'vbscript', 'vbulletin', 'vc6', 'vc8', 'vcalendar', 'vcbuild', 'vcg', 'vcl', 'vcproj',
            'vcredist', 'vcxproj', 'vdm++', 'vector', 'vector-graphics', 'vectorization', 'velocis-rds', 'velocity',
            'vera++', 'verbosity', 'verification', 'version', 'version-control', 'version-detection',
            'version-numbering', 'versioning', 'versions', 'vertex', 'vertex-array', 'vertex-attributes',
            'vertex-buffer', 'vertex-shader', 'vertical-alignment', 'vertices', 'verysleepy', 'vfs', 'vfw', 'vi',
            'video', 'video-capture', 'video-card', 'video-codecs', 'video-encoding', 'video-game-consoles',
            'video-processing', 'video-streaming', 'view', 'viewing', 'viewport', 'views', 'vigenere', 'vim',
            'vim-plugin', 'vim-syntax-highlighting', 'viola-jones', 'viper', 'virtual-address-space',
            'virtual-destructor', 'virtual-functions', 'virtual-inheritance', 'virtual-keyboard', 'virtual-machine',
            'virtual-memory', 'virtual-method', 'virtualalloc', 'virtualbox', 'virtualenv', 'virtualization',
            'virtualquery', 'virus', 'visibility', 'visio', 'vision', 'visitor', 'visitor-pattern', 'visitors',
            'vista64', 'visual-age', 'visual-assist', 'visual-c++', 'visual-c++-2005', 'visual-c++-2008',
            'visual-c++-2008-express', 'visual-c++-2010', 'visual-c++-2010-express', 'visual-c++-2012',
            'visual-leak-detector', 'visual-sourcesafe', 'visual-studio', 'visual-studio-2003', 'visual-studio-2005',
            'visual-studio-2008', 'visual-studio-2008-sp1', 'visual-studio-2010', 'visual-studio-2010-sp1',
            'visual-studio-2012', 'visual-studio-2013', 'visual-studio-2015', 'visual-studio-6', 'visual-studio-addins',
            'visual-studio-debugging', 'visual-studio-express', 'visual-studio-extensions', 'visual-studio-macros',
            'visual-studio-project', 'visual-styles', 'visualization', 'visualizer', 'visualstatemanager', 'visualsvn',
            'vlc', 'vm-implementation', 'vmime', 'vmware', 'vocabulary', 'void-pointers', 'voip', 'voltdb', 'volume',
            'volume-shadow-service', 'vorbis', 'voronoi', 'voxel', 'vp8', 'vptr', 'vrml', 'vs-unit-testing-framework',
            'vshost.exe', 'vsperfmon', 'vsprops', 'vst', 'vsx', 'vt100', 'vtable', 'vtd-xml', 'vtk', 'vtune', 'vxworks',
            'w32', 'waf', 'waitformultipleobjects', 'waitforsingleobject', 'waitpid', 'wallpaper', 'warnings', 'was',
            'wasapi', 'watch', 'watchdog', 'watchpoint', 'watcom', 'wav', 'waveform', 'wavefront', 'wavelet', 'waveout',
            'waveoutwrite', 'wbem', 'wcf', 'wcf-binding', 'wchar', 'wchar-t', 'wdf', 'wdk', 'weak-ptr',
            'weak-references', 'web', 'web-applications', 'web-control', 'web-crawler', 'web-scraping', 'web-services',
            'webbrowser-control', 'webcam', 'webclient', 'webdav', 'webforms', 'webkit', 'webos', 'webp', 'webpage',
            'webrtc', 'webserver', 'webservice-client', 'website', 'websocket', 'webview', 'wexitstatus', 'wfp', 'wget',
            'wh-keyboard-ll', 'which', 'while-loop', 'white-box-testing', 'whiteboard', 'whitespace', 'whm', 'wia',
            'wic', 'widechar', 'widescreen', 'widestring', 'widget', 'wifi', 'wifstream', 'wiimote', 'wiiuse', 'wiki',
            'wildcard', 'win32-process', 'win32gui', 'win32ole', 'win64', 'winapi', 'winavr', 'windbg', 'windmill',
            'window', 'window-chrome', 'window-decoration', 'window-handles', 'window-management', 'window-managers',
            'window-messages', 'window-resize', 'windowed', 'windowing', 'windows', 'windows-7', 'windows-7-x64',
            'windows-8', 'windows-95', 'windows-applications', 'windows-ce', 'windows-console', 'windows-embedded',
            'windows-error-reporting', 'windows-explorer', 'windows-forms-designer', 'windows-installer',
            'windows-kernel', 'windows-live-messenger', 'windows-media-encoder', 'windows-media-player',
            'windows-messages', 'windows-mobile', 'windows-mobile-5.0', 'windows-mobile-6.5', 'windows-networking',
            'windows-nt', 'windows-phone', 'windows-phone-8', 'windows-ribbon-framework', 'windows-rt',
            'windows-runtime', 'windows-server', 'windows-server-2000', 'windows-server-2003', 'windows-server-2008',
            'windows-server-2008-r2', 'windows-server-2012', 'windows-services', 'windows-shell', 'windows-socket-api',
            'windows-store', 'windows-store-apps', 'windows-update', 'windows-vista', 'windows-xp',
            'windows-xp-embedded', 'windows-xp-sp3', 'wine', 'winforms', 'winforms-interop', 'winhelp', 'winhttp',
            'winhttprequest', 'wininet', 'winmain', 'winmm', 'winpcap', 'winpe', 'winrar', 'winreg', 'winrt-async',
            'winrt-xaml', 'winsnmp', 'winsock', 'winsock2', 'winsockets', 'winsxs', 'winusb', 'wireless', 'wireshark',
            'wix', 'wizard', 'wlanapi', 'wm-paint', 'wma', 'wmdc', 'wmf', 'wmi', 'wmi-query', 'wmic', 'wmp', 'wndproc',
            'wnet', 'wofstream', 'wolfram-mathematica', 'word', 'word-boundary', 'word-count', 'word-processor',
            'word-vba', 'word-wrap', 'words', 'workbench', 'worker-process', 'worker-thread', 'workflow',
            'working-directory', 'worksheet', 'wostringstream', 'wow64', 'wpd', 'wpf', 'wrap', 'wrapper', 'wrapping',
            'writefile', 'writetofile', 'wrl', 'ws-ex-layered', 'ws-security', 'wsacleanup', 'wsastartup', 'wsdl',
            'wsh', 'wso2', 'wso2carbon', 'wstring', 'wt', 'wtl', 'wtsapi32', 'wubi', 'wwsapi', 'wxformbuilder',
            'wxglade', 'wxglcanvas', 'wxhttp', 'wxmathplot', 'wxnotebook', 'wxpython', 'wxtextctrl', 'wxwidgets', 'x++',
            'x-macros', 'x11', 'x264', 'x3d', 'x509', 'x509certificate', 'x86', 'x86-16', 'x86-64', 'xa', 'xalan',
            'xamarin-studio', 'xaml', 'xampp', 'xaudio2', 'xbee', 'xcb', 'xcode', 'xcode3.2', 'xcode4', 'xcode4.2',
            'xcode4.3', 'xcode4.5', 'xcode4.6', 'xcodebuild', 'xerces', 'xerces-c', 'xgettext', 'xinput', 'xlc', 'xlib',
            'xll', 'xls', 'xlsb', 'xlsx', 'xlw', 'xml', 'xml-formatting', 'xml-parsing', 'xml-rpc', 'xml-serialization',
            'xmldocument', 'xmlhttprequest', 'xmlreader', 'xmlunit', 'xmm', 'xmpp', 'xna', 'xna-math-library',
            'xp-theme', 'xpath', 'xpcom', 'xpressive', 'xps', 'xqilla', 'xquery', 'xrc', 'xs', 'xsd', 'xsd-1.1',
            'xserver', 'xsl-fo', 'xslt', 'xslt-2.0', 'xss', 'xt', 'xterm', 'xtext', 'xubuntu', 'xul', 'xz',
            'y-combinator', 'yacc', 'yahoo', 'yajl', 'yaml', 'yaml-cpp', 'youtube', 'youtube-api', 'yuv', 'z3', 'z80',
            'zbar', 'zbuffer', 'zero', 'zero-copy', 'zeromq', 'zip', 'zkcm', 'zlib', 'zombie-process', 'zoom',
            'zooming', 'zos', 'zxing']

stem_tag_list = []
st = LancasterStemmer()


def cpp_tag(text):
    wordlist = []
    # 结构体名
    pattern = re.compile(r'struct[ \n\t]+[a-zA-Z0-9_]+[ \n\t]*{')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        n = name.find('{')
        if n==-1:
            print(name)
            wordlist.append(name)
        else:
            name = name[:n].replace(' ', '').replace('\t', '').replace('\n', '')
            print(name)
            wordlist.append(name)

    # 单行注释
    pattern = re.compile(r'//.*')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = re.sub("[\s+\!\/\.,$%^*(+\"\'<>()#]+|[+——！，。？、~@#￥%……&*（）]+", " ", r)
        print(name)
        list = name.split()
        for item in list:
            print(item)
            #wordlist.append(item)

    # 多行注释
    pattern = re.compile(r'\/\*[^\*]*\*\/')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = re.sub("[\s+\!\/\.,$%^*(+\"\'<>()#]+|[+——！，。？、~@#￥%……&*（）]+", " ", r)
        print(name)
        list = name.split()
        for item in list:
            print(item)
            #wordlist.append(item)

    # 函数名
    pattern = re.compile(r'[a-zA-Z0-9_]+[ \t]+[a-zA-Z0-9_]+[ \t\n]*\(.*\)[ \t\n]*{')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        n = name.find('(')
        if n==-1:
            print(name)
            wordlist.append(name)
        else:
            name = name[:n].replace(' ', '').replace('\t', '').replace('\n', '')
            print(name)
            wordlist.append(name)

    # 成员函数名
    pattern = re.compile(r'[a-zA-Z0-9_]+::[a-zA-Z0-9_]+[ \t\n]*\(.*\)[ \t\n]*{')
    res = pattern.findall(text)
    for r in res:
        print(r)
        n1 = r.find(':')
        n2 = r.find('(')
        name = r[n1+2 : n2].replace(' ', '').replace('\t', '').replace('\n', '')
        print(name)
        wordlist.append(name)

    # 类名
    pattern = re.compile(r'class[ \t\n]+[a-zA-Z0-9_]+[ \t\n]*{')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        n = name.find('{')
        if n==-1:
            print(name)
            wordlist.append(name)
        else:
            name = name[:n].replace(' ', '').replace('\t', '').replace('\n', '')
            print(name)
            wordlist.append(name)

    # 全局声明
    pattern = re.compile(r'#define[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        print(name)
        wordlist.append(name)

    pattern = re.compile(r'typedef[ \t\n]+[a-zA-Z0-9_]+[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[2]
        print(name)
        wordlist.append(name)

    pattern = re.compile(r'const[ \t\n]+[a-zA-Z0-9_]+[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[2]
        print(name)
        wordlist.append(name)

    return wordlist

def java_tag(text):
    wordlist = []

    pattern = re.compile(r'class[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        print(name)
        wordlist.append(name)

    pattern = re.compile(r'[a-zA-Z0-9_]+[ \t]+[a-zA-Z0-9_]+[ \t\n]*\(.*\)[ \t\n]*{')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        n = name.find('(')
        if n == -1:
            print(name)
            wordlist.append(name)
        else:
            name = name[:n].replace(' ', '').replace('\t', '').replace('\n', '')
            print(name)
            wordlist.append(name)

    pattern = re.compile(r'enum[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        print(name)
        wordlist.append(name)

    pattern = re.compile(r'final[ \t\n]+[a-zA-Z0-9_]+[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[2]
        print(name)
        wordlist.append(name)

    pattern = re.compile(r'package[ \t\n]+[a-zA-Z0-9_\.]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        t = r.split(' ')[1]
        words = t.split('.')
        for w in words:
            print(w)
            wordlist.append(w)

    # 单行注释
    pattern = re.compile(r'//.*')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = re.sub("[\s+\!\/\.,$%^*(+\"\'<>()#]+|[+——！，。？、~@#￥%……&*（）]+", " ", r)
        print(name)
        list = name.split()
        for item in list:
            print(item)
            #wordlist.append(item)

    # 多行注释
    pattern = re.compile(r'\/\*[^\*]*\*\/')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = re.sub("[\s+\!\/\.,$%^*(+\"\'<>()#]+|[+——！，。？、~@#￥%……&*（）]+", " ", r)
        print(name)
        list = name.split()
        for item in list:
            print(item)
            #wordlist.append(item)

    print(wordlist)
    return wordlist

def python_tag(text):
    wordlist = []

    pattern = re.compile(r'def[ \t\n]+[a-zA-Z0-9_]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = r.split(' ')[1]
        print(name)
        wordlist.append(name)

    pattern = re.compile(r'import[ \t\n]+[a-zA-Z0-9_\.]+')
    res = pattern.findall(text)
    for r in res:
        print(r)
        t = r.split(' ')[1]
        words = t.split('.')
        for w in words:
            print(w)
            wordlist.append(w)

    # 单行注释
    pattern = re.compile(r'#.*')
    res = pattern.findall(text)
    for r in res:
        print(r)
        name = re.sub("[\s+\!\/\.,$%^*(+\"\'<>()#]+|[+——！，。？、~@#￥%……&*（）]+", " ", r)
        print(name)
        list = name.split()
        for item in list:
            print(item)
            #wordlist.append(item)

    print(wordlist)
    return wordlist

def find_tag(file, writer):
    f = open(file, "r", encoding="utf-8")
    text = f.read()

    (filepath, filename) = os.path.split(file)
    title = filename.split('.')[0]
    suffix = filename.split('.')[1]

    if suffix == 'cpp' or suffix == 'c' or suffix == 'h':
        wordlist = cpp_tag(text)
    elif suffix == 'java':
        wordlist = java_tag(text)
    elif suffix == 'py':
        wordlist = python_tag(text)

    taglist = []
    for w in wordlist:
        word = w.lower()#转小写
        word = word.replace("-", "").replace("_", "")#去连字符
        word = st.stem(word)#词干化
        if word in stem_tag_list:  # 检测词语文本是否在stem_tag_list中。是则将对应的“原标签名” 写入
            taglist.append(w + "#" + tag_list[stem_tag_list.index(word)])

    t = title.lower()
    t = t.replace("-", "").replace("_", "")
    t = st.stem(t)
    if t in stem_tag_list:  #检查文件名本身是否在列表中，
        taglist.append(title + "#" + tag_list[stem_tag_list.index(t)])
    else:
        1
        #taglist.append(t)

    print(taglist)
    # 去重
    taglist = list(set(taglist))
    lines = text.split('\n')
    for item in taglist:    #写入csv文件
        name = item.split('#')[0]
        tag_name = item.split('#')[1]
        line_no = 0
        for line in lines:
            if name in line:
                line_no = lines.index(line)+1
                break
        writer.writerow([filename, tag_name, line_no, file.replace("G:/data/","")])


def search_file(file, writer):
    if os.path.isdir(file):
        subfiles = os.listdir(file)
        subfiles = [file + '/' + i for i in subfiles]
        for subfile in subfiles:
            search_file(subfile, writer)
    else:
        print("    " + str(file))
        try:
            find_tag(file, writer)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    print(tag_list)
    print(len(tag_list))

    for tag in tag_list:  # 将原有的tag统一删去标点，并进行词干化，保存在stem_tag列表中
        stem_tag_list.append(st.stem(tag.replace("-", "").replace("_", "").replace(".", "")))

    print(stem_tag_list)
    print(len(stem_tag_list))

    path = 'G:/data'  # 此处填github代码存放的路径
    projects_name = os.listdir(path)
    projects = [path + '/' + i for i in projects_name]
    num = 0
    for project in projects:
        # 此处填输出文件路径
        ft = open("C:/Users/CJY/Desktop/Project_tags/" + str(projects_name[num], ) + ".csv", "w", newline='',
                  encoding="utf-8")  # 创建新的csv数据文件（用项目名为其命名）
        writer = csv.writer(ft)
        writer.writerow(('file_name', 'tag_name', 'line', 'path'))  # 写入第一行标签信息
        print(project)
        search_file(project, writer)
        ft.close()
        num = num + 1


    # # 以下用于将文件数据导入neo4j
    # graph = Graph(
    #     "http://localhost:7474",
    #     username="",
    #     password=""
    # )
    #
    # path = "C:/Users/CJY/Desktop/Project_tags"
    # files = os.listdir(path)
    # files = [path + '/' + i for i in files]
    #
    # for file_path in files:
    #     print(file_path)
    #     (filepath, tempfilename) = os.path.split(file_path)
    #     (project_name, extension) = os.path.splitext(tempfilename)
    #     #print(filepath+"  "+filename+"  "+extension)
    #     f = open(file_path, 'r', encoding='utf-8')
    #     csv_reader_lines = csv.reader(f)
    #
    #     p_node = Node("Project", project_name=project_name)#创建项目节点
    #     graph.create(p_node)
    #
    #     next(csv_reader_lines)  # 跳过第一行的标签信息
    #     file_list = []
    #     count = 1
    #     for line in csv_reader_lines:
    #         print(str(count) + str(line))
    #         file_name = line[0]
    #         if file_name not in file_list:
    #             f_node = Node("File", file_name = file_name, parent_project = project_name)
    #             graph.create(f_node)#创建文件结点
    #             rel = Relationship(p_node, "contains", f_node)
    #             graph.create(rel)#创建项目“包含”文件关系
    #             file_list.append(file_name)
    #         tag_name = line[1]
    #         instr = """
    #             match (a:File),(b:Tag)
    #             where a.file_name = '""" + file_name + """' and b.tag_name = '""" + tag_name + """'
    #             create (a)-[r:has_tag]->(b)
    #         """
    #         graph.run(instr)#创建文件到标签的has_tag关系
    #         count = count + 1
